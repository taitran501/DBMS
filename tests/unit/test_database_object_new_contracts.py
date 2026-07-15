import pytest

from dbms.database_object.constraint_management import Constraint, ConstraintEnforcer
from dbms.database_object.data_type_management import DataTypeDescriptor, DataTypeManager, TypeConverter
from dbms.database_object.index_management import Index, IndexDescriptor, IndexMaintainer, IndexManager
from dbms.database_object.metadata_management import DependencyManager, MetadataManager, SystemCatalog
from dbms.database_object.schema_management.schema import ColumnSchema, TableSchema
from dbms.database_object.table_management import TableManager
from dbms.database_object.trigger_management import TriggerManager
from dbms.errors import DependencyExistsError, ObjectNotFoundError, RowNotFoundError
from dbms.subsystems import DatabaseObjectManager


def test_catalog_mutations_and_dependency_traversal_return_consistent_results():
    catalog = SystemCatalog()
    catalog.add_metadata("table:t", 1)
    catalog.update_metadata("table:t", 2)
    assert catalog.get_metadata("table:t") == 2
    assert catalog.remove_metadata("table:t") == 2
    with pytest.raises(ObjectNotFoundError): catalog.update_metadata("missing", 1)
    with pytest.raises(ObjectNotFoundError): catalog.remove_metadata("missing")

    deps = DependencyManager()
    deps.add_metadata_dependency("view:v", "table:t")
    deps.add_metadata_dependency("trigger:x", "view:v")
    assert deps.get_metadata_dependents("table:t", recursive=True) == ("view:v", "trigger:x")
    assert deps.get_metadata_dependencies("view:v") == ("table:t",)
    deps.remove_metadata_dependent("view:v")
    assert deps.get_metadata_dependents("table:t") == ()


def test_metadata_blocks_and_cascades_real_dependents():
    metadata = MetadataManager()
    metadata.register_metadata("table", "t", object())
    metadata.register_metadata("view", "v", object(), ["table:t"])
    with pytest.raises(DependencyExistsError): metadata.remove_metadata("table", "t")
    metadata.remove_metadata("table", "t", cascade=True)
    assert metadata.objects == {}


def test_type_registry_rejects_duplicates_and_converts_supported_values():
    types = DataTypeManager()
    types.register_type(DataTypeDescriptor("FLOAT", float, nullable=False))
    with pytest.raises(ValueError): types.register_type(DataTypeDescriptor("FLOAT"))
    with pytest.raises(ValueError): types.resolve("JSON")
    assert types.validate_value(types.resolve("FLOAT"), None) is False
    converter = TypeConverter()
    assert converter.convert_type_value("BOOLEAN", "false") is False
    assert converter.convert_type_value("TEXT", 3) == "3"
    assert converter.convert_type_value("INT", "bad") == "bad"
    custom = types.register_type(DataTypeDescriptor("CUSTOM"))
    assert types.validate_value(custom, object()) is True


def test_constraint_enforcer_applies_not_null_unique_and_check_rules():
    enforcer = ConstraintEnforcer()
    assert enforcer.validate_constraint(Constraint("n", "NOT_NULL", ["x"]).descriptor, {"x": None}) is False
    assert enforcer.validate_constraint(Constraint("u", "UNIQUE", ["x"]).descriptor, {"x": None}, ({"x": None},)) is True
    assert enforcer.validate_constraint(Constraint("u", "UNIQUE", ["x"]).descriptor, {"x": 1}, ({"x": 1},)) is False
    assert enforcer.validate_constraint(Constraint("c", "CHECK", [], predicate=lambda row: row["x"] > 0).descriptor, {"x": -1}) is False


def test_index_maintenance_updates_entries_and_rolls_back_partial_failure():
    descriptor = IndexDescriptor("u", "HASH", ("id",), True)
    maintainer = IndexMaintainer()
    maintainer.maintain_index_entry(descriptor, (1,), 1, "INSERT")
    maintainer.maintain_index_entry(descriptor, (1,), 1, "UPDATE")
    with pytest.raises(ValueError, match="conflict"): maintainer.maintain_index_entry(descriptor, (1,), 2, "INSERT")
    maintainer.maintain_index_entry(descriptor, (1,), 1, "DELETE")
    assert maintainer.find_row_ids_by_key((1,)) == ()
    with pytest.raises(ValueError, match="Unsupported"): maintainer.maintain_index_entry(descriptor, (1,), 1, "MERGE")

    class Reject(IndexMaintainer):
        def maintain_index_entry(self, index, key, row_id, op):
            if index.name == "bad" and op == "INSERT": raise RuntimeError("bad")
            super().maintain_index_entry(index, key, row_id, op)
    manager = IndexManager()
    first = Index("ok", "HASH", ["id"])
    manager.create_index("t", first)
    manager.create_index("t", Index("bad", "HASH", ["id"], maintainer=Reject()))
    with pytest.raises(RuntimeError): manager.maintain_table_indexes("t", {"id": 1}, 1, "INSERT")
    assert first.maintainer.find_row_ids_by_key((1,)) == ()
    tree = Index("tree", "B_TREE", ["id"]); manager.create_index("t", tree)
    tree.maintainer.maintain_index_entry(tree.descriptor, (1,), 1, "INSERT"); tree.maintainer.maintain_index_entry(tree.descriptor, (3,), 3, "INSERT")
    assert manager.find_indexed_row_ids_in_range("t", "tree", (1,), (2,)) == (1,)
    with pytest.raises(ValueError, match="B_TREE"): manager.find_indexed_row_ids_in_range("t", "ok")


def test_table_manager_rejects_missing_rows_and_filters_matching_rows():
    manager = TableManager(); table = manager.create_table("s", "t", TableSchema("t", [ColumnSchema("x", "INT")]))
    with pytest.raises(RowNotFoundError): manager.update_row(table, 1, {})
    with pytest.raises(RowNotFoundError): manager.delete_row(table, 1)
    manager.insert_row(table, {"x": 1}); manager.insert_row(table, {"x": 2})
    assert manager.update_row(table, 1, {"x": 3}) == {"x": 1}
    assert manager.delete_row(table, 2) == {"x": 2}
    assert len(manager.select_rows(table, lambda row: row["x"] > 1)) == 1
    with pytest.raises(ValueError, match="ambiguous"):
        manager.find_table("missing")


def test_facade_rejects_invalid_rows_and_rolls_back_trigger_failures():
    from dbms.database_object.index_management import IndexManager
    db = DatabaseObjectManager(SystemCatalog(), IndexManager())
    db.provision_table("s", "t", TableSchema("t", [ColumnSchema("id", "INT", False)]))
    with pytest.raises(ValueError, match="Unknown"): db.insert_row("t", {"other": 1})
    with pytest.raises(ValueError, match="cannot be null"): db.insert_row("t", {})
    with pytest.raises(ValueError, match="Invalid"): db.insert_row("t", {"id": "bad"})
    row_id = db.insert_row("t", {"id": 1})
    with pytest.raises(RowNotFoundError): db.update_row("t", 99, {"id": 2})
    with pytest.raises(RowNotFoundError): db.delete_row("t", 99)
    db.provision_trigger("t", "fail-update", "UPDATE", "AFTER", lambda ctx: (_ for _ in ()).throw(RuntimeError("stop")))
    with pytest.raises(RuntimeError): db.update_row("t", row_id, {"id": 2})
    assert db.select_rows("t")[0]["id"] == 1

    db.provision_trigger("t", "fail-insert", "INSERT", "AFTER", lambda ctx: (_ for _ in ()).throw(RuntimeError("stop")))
    with pytest.raises(RuntimeError): db.insert_row("t", {"id": 3})
    assert [row["id"] for row in db.select_rows("t")] == [1]


def test_create_trigger_rejects_unsupported_event_and_timing():
    manager = TriggerManager()
    with pytest.raises(ValueError, match="event"): manager.create_trigger("t", "x", "SELECT", "AFTER", None)
    with pytest.raises(ValueError, match="timing"): manager.create_trigger("t", "x", "INSERT", "DURING", None)


def test_configuration_and_owner_updates_apply_valid_changes_and_reject_invalid_changes():
    from dbms.database_object.database_management import DatabaseConfiguration, DatabaseManager
    from dbms.database_object.schema_management import SchemaManager
    databases = DatabaseManager(); databases.create_database("db")
    assert databases.alter_configuration("db", DatabaseConfiguration(page_size=8192)).descriptor.config.page_size == 8192
    with pytest.raises(ValueError): databases.alter_configuration("db", DatabaseConfiguration(page_size=0))
    schemas = SchemaManager(); schemas.create_schema("db", "public"); schemas.change_schema_owner("db", "public", "alice")
    assert schemas.owners[("db", "public")] == "alice"
    class DenyOwner:
        def can_create_schema(self, *args): return True
        def can_drop_schema(self, *args): return True
        def can_change_schema_owner(self, *args): return False
    denied = SchemaManager(ownership_policy=DenyOwner()); denied.create_schema("db", "s")
    with pytest.raises(PermissionError, match="owner"): denied.change_schema_owner("db", "s", "bob")
