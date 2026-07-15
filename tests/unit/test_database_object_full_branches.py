import pytest

from dbms.database_object.column_management import Column, ColumnDescriptor, ColumnManager
from dbms.database_object.constraint_management import Constraint, ConstraintDescriptor, ConstraintManager
from dbms.database_object.data_type_management import DataType, DataTypeDescriptor, TypeConverter
from dbms.database_object.database_management import DatabaseDescriptor, DatabaseManager, DatabaseRegistry
from dbms.database_object.index_management import Index, IndexDescriptor, IndexManager
from dbms.database_object.metadata_management import DependencyManager, MetadataManager, StatisticsManager
from dbms.database_object.relationship_management import Relationship, RelationshipDescriptor
from dbms.database_object.schema_management import SchemaCatalog, SchemaManager, SchemaMigrationLedger, SchemaOwnershipPolicy
from dbms.database_object.schema_management.schema import TableSchema
from dbms.database_object.stored_procedure import ProcedureDescriptor, StoredProcedure, StoredProcedureManager
from dbms.database_object.table_management import Table
from dbms.database_object.trigger_management import Trigger, TriggerDescriptor, TriggerManager
from dbms.database_object.view_management import View, ViewDependencyGraph, ViewManager
from dbms.errors import TriggerNotExecutableError


def test_construct_value_objects_accepts_descriptors_and_defaults():
    assert Column(ColumnDescriptor("id", "INT")).name == "id"
    assert Constraint(ConstraintDescriptor("pk", "PRIMARY_KEY", ["id"])).name == "pk"
    assert DataType(DataTypeDescriptor("CUSTOM")).name == "CUSTOM"
    assert Index(IndexDescriptor("idx", "HASH", ["id"])).name == "idx"
    assert Relationship(RelationshipDescriptor("fk", "a", "b", "N_1")).name == "fk"
    assert StoredProcedure(ProcedureDescriptor("p", [], "pass")).name == "p"
    assert Trigger(TriggerDescriptor("tr", "INSERT", "AFTER", "pass")).name == "tr"
    assert View("v", "SELECT 1").select_query == "SELECT 1"
    assert Table("t", TableSchema("t", [])).descriptor.name == "t"
    assert DatabaseDescriptor("db").config.page_size == 4096


def test_manager_create_rejects_duplicates_and_lookup_returns_registered_objects():
    columns = ColumnManager()
    columns.columns["empty"] = []
    with pytest.raises(ValueError):
        columns.get_column("empty", "missing")
    columns.add_column("t", Column("a", "INT"))
    columns.add_column("t", Column("b", "INT"))
    with pytest.raises(ValueError, match="already exists"):
        columns.add_column("t", Column("a", "INT"))
    assert columns.get_column("t", "b").name == "b"
    columns.drop_column("missing", "a")

    constraints = ConstraintManager()
    constraints.constraints["empty"] = []
    with pytest.raises(ValueError):
        constraints.get_constraint("empty", "missing")
    constraints.create_constraint("t", Constraint("a", "CHECK", []))
    constraints.create_constraint("t", Constraint("b", "CHECK", []))
    assert constraints.get_constraint("t", "b").name == "b"
    constraints.drop_constraint("t", "a")

    indexes = IndexManager()
    indexes.indexes["empty"] = []
    with pytest.raises(ValueError):
        indexes.get_index("empty", "missing")
    indexes.create_index("t", Index("a", "HASH", []))
    indexes.create_index("t", Index("b", "HASH", []))
    assert indexes.get_index("t", "b").name == "b"
    indexes.drop_index("t", "a")
    indexes.maintain_table_indexes("missing", {}, 1, "insert")


def test_repeated_registry_and_dependency_operations_remain_idempotent():
    registry = DatabaseRegistry()
    descriptor = DatabaseDescriptor("db")
    registry.register_database(descriptor)
    assert registry.find_database_by_name("db") is descriptor
    registry.remove_database("db")
    registry.remove_database("db")

    dependencies = DependencyManager()
    dependencies.add_metadata_dependency("view:v", "table:t")
    dependencies.add_metadata_dependency("view:v", "table:t")
    assert dependencies.dependencies["table:t"] == ["view:v"]

    stats = StatisticsManager()
    stats.update_statistics("t", "rows", 1)
    stats.update_statistics("t", "rows", 2)
    assert stats.get_statistics("t", "rows") == 2

    metadata = MetadataManager(dependency_manager=dependencies, statistics_manager=stats)
    metadata.register_metadata("table", "t", descriptor)
    with pytest.raises(ValueError, match="already exists"):
        metadata.register_metadata("table", "t", descriptor)
    metadata.remove_metadata("table", "t")
    metadata.remove_metadata("table", "t")
    with pytest.raises(ValueError, match="not found"):
        metadata.get_metadata("table", "t")


def test_manager_noop_operations_preserve_state_and_policy_failures_raise_errors():
    db = DatabaseManager()
    db.create_database("db")
    with pytest.raises(ValueError, match="already exists"):
        db.create_database("db")

    class DenyPolicy(SchemaOwnershipPolicy):
        def __init__(self, create=True, drop=True):
            self.create = create
            self.drop = drop

        def can_create_schema(self, actor_id, database_id):
            return self.create

        def can_drop_schema(self, actor_id, schema_name):
            return self.drop

    with pytest.raises(PermissionError, match="creation"):
        SchemaManager(ownership_policy=DenyPolicy(create=False)).create_schema("db", "s")
    schema_manager = SchemaManager(SchemaCatalog(), DenyPolicy(drop=False), SchemaMigrationLedger())
    schema_manager.create_schema("db", "s")
    with pytest.raises(PermissionError, match="deletion"):
        schema_manager.drop_schema("db", "s")
    schema_manager.drop_schema("missing", "s")

    procedures = StoredProcedureManager()
    procedures.create_procedure("s", "p", [], "pass")
    with pytest.raises(ValueError, match="already exists"):
        procedures.create_procedure("s", "p", [], "pass")
    procedures.drop_procedure("missing", "p")

    triggers = TriggerManager()
    triggers.triggers["empty"] = []
    with pytest.raises(ValueError):
        triggers.get_trigger("empty", "missing")
    triggers.create_trigger("t", "tr", "INSERT", "AFTER", "pass")
    with pytest.raises(ValueError, match="already exists"):
        triggers.create_trigger("t", "tr", "INSERT", "AFTER", "pass")
    triggers.drop_trigger("missing", "tr")
    with pytest.raises(TriggerNotExecutableError):
        triggers.publish_table_event("t", "insert")
    assert triggers.publish_table_event("t", "update") == []

    graph = ViewDependencyGraph()
    graph.add_view_dependency("v", "t1")
    graph.add_view_dependency("v", "t2")
    views = ViewManager(graph)
    views.create_view("s", "v", "SELECT 1")
    with pytest.raises(ValueError, match="already exists"):
        views.create_view("s", "v", "SELECT 1")
    views.drop_view("missing", "v")


def test_convert_int_preserves_existing_integer_value():
    assert TypeConverter().convert_type_value("INT", 1) == 1


def test_lookup_drop_and_facade_delegation_follow_manager_contracts():
    columns = ColumnManager()
    columns.add_column("t", Column("a", "INT"))
    with pytest.raises(ValueError):
        columns.get_column("t", "missing")

    constraints = ConstraintManager()
    constraints.create_constraint("t", Constraint("a", "CHECK", []))
    with pytest.raises(ValueError):
        constraints.get_constraint("t", "missing")

    indexes = IndexManager()
    indexes.create_index("t", Index("a", "HASH", []))
    with pytest.raises(ValueError):
        indexes.get_index("t", "missing")

    catalog = SchemaCatalog()
    catalog.remove_schema("missing")
    assert SchemaOwnershipPolicy().can_change_schema_owner("a", "s", "b") is True

    procedures = StoredProcedureManager()
    direct = StoredProcedure("direct", [], "pass")
    direct.executor.execute_procedure_body(direct.descriptor, [])
    procedures.create_procedure("s", "a", [], "pass")
    procedures.create_procedure("s", "b", [], "pass")
    assert procedures.get_procedure("s", "b").name == "b"

    triggers = TriggerManager()
    direct_trigger = Trigger("direct", "INSERT", "AFTER", "pass")
    with pytest.raises(TriggerNotExecutableError):
        direct_trigger.executor.execute_trigger_action(direct_trigger.descriptor)
    triggers.create_trigger("t", "a", "INSERT", "AFTER", "pass")
    triggers.create_trigger("t", "b", "UPDATE", "AFTER", "pass")
    assert triggers.get_trigger("t", "b").name == "b"
    with pytest.raises(ValueError):
        triggers.get_trigger("t", "missing")

    views = ViewManager()
    views.create_view("s", "v", "SELECT 1")
    assert views.get_view("s", "v").name == "v"

    from dbms.database_object.table_management import TableManager
    tables = TableManager()
    tables.tables["empty"] = {}
    tables.drop_table("empty", "missing")
    tables.drop_table("missing", "missing")

    from dbms.database_object.metadata_management import Catalog
    from dbms.subsystems import DatabaseObjectManager

    class LegacyIndexes:
        def create_index(self, *args):
            self.created = args

        def maintain_index(self, *args):
            self.maintained = args

    legacy = LegacyIndexes()
    facade = DatabaseObjectManager(Catalog(), legacy)
    schema = TableSchema("legacy", [])
    facade.create_table(schema)
    assert facade.has_table("legacy") is True
    assert facade.get_table("legacy") is schema
    facade.create_index("idx", "legacy", "id")
    facade.maintain_index("idx", 1, 2, "INSERT")
    assert legacy.created == ("idx", "legacy", "id")
    assert legacy.maintained == ("idx", 1, 2, "INSERT")
