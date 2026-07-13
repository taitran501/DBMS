import pytest

from dbms.database_object.constraint_management import Constraint, ConstraintEnforcer
from dbms.database_object.index_management import Index, IndexMaintainer
from dbms.database_object.metadata_management import Catalog, MetadataManager
from dbms.database_object.schema_management.schema import ColumnSchema, TableSchema
from dbms.subsystems import DatabaseObjectManager


class RecordingMaintainer(IndexMaintainer):
    def __init__(self):
        self.calls = []

    def maintain(self, index, key, row_id, op):
        self.calls.append((index.name, key, row_id, op))


class RejectingEnforcer(ConstraintEnforcer):
    def validate(self, descriptor, value_dict):
        return value_dict.get("id", 0) > 0


@pytest.fixture
def manager():
    catalog = Catalog()
    return DatabaseObjectManager(catalog, __import__(
        "dbms.database_object.index_management", fromlist=["IndexManager"]
    ).IndexManager(), metadata_manager=MetadataManager(catalog))


def test_database_schema_and_table_sequence_synchronizes_metadata(manager):
    manager.provision_database("shop")
    manager.provision_schema("shop", "public")
    table = manager.provision_table(
        "public", "users", TableSchema("users", [ColumnSchema("id", "INT"), ColumnSchema("name", "TEXT")])
    )

    assert manager.metadata_manager.get("database", "shop").name == "shop"
    assert manager.metadata_manager.get("schema", "public").name == "public"
    assert manager.metadata_manager.get("table", "users") is table.descriptor
    assert manager.metadata_manager.dependency_manager.dependencies["database:shop"] == ["schema:public"]
    assert manager.metadata_manager.dependency_manager.dependencies["schema:public"] == ["table:users"]
    assert [column.name for column in manager.column_manager.columns["users"]] == ["id", "name"]
    assert manager.metadata_manager.statistics_manager.get_statistics("users", "row_count") == 0


def test_table_sequence_rejects_unknown_type_before_side_effect(manager):
    schema = TableSchema("bad", [ColumnSchema("payload", "JSONB")])
    with pytest.raises(ValueError, match="not registered"):
        manager.provision_table("public", "bad", schema)
    assert "public" not in manager.table_manager.tables
    assert "table:bad" not in manager.metadata_manager.objects


def test_advanced_object_sequence_registers_dependencies(manager):
    manager.provision_view("public", "active_users", "SELECT * FROM users", ["table:users"])
    manager.provision_procedure("public", "archive", [], "DELETE FROM users", ["table:users"])
    manager.provision_trigger("users", "audit", "INSERT", "AFTER", "audit()")

    dependents = manager.metadata_manager.dependency_manager.dependencies["table:users"]
    assert dependents == ["view:active_users", "procedure:archive", "trigger:audit"]


def test_runtime_sequence_runs_before_constraint_index_after_and_statistics(manager):
    events = []
    before = manager.provision_trigger("users", "before", "INSERT", "BEFORE", "check()")
    after = manager.provision_trigger("users", "after", "INSERT", "AFTER", "audit()")
    before.executor.execute = lambda descriptor: events.append(descriptor.name)
    after.executor.execute = lambda descriptor: events.append(descriptor.name)

    maintainer = RecordingMaintainer()
    manager.index_manager.create_index("users", Index("idx_users_id", "B_TREE", ["id"], maintainer=maintainer))
    manager.constraint_manager.create_constraint(
        "users", Constraint("positive_id", "CHECK", ["id"], RejectingEnforcer())
    )

    matched = manager.apply_table_event("users", "insert", {"id": 7}, 42)

    assert events == ["before", "after"]
    assert matched == [after]
    assert maintainer.calls == [("idx_users_id", (7,), 42, "INSERT")]
    assert manager.metadata_manager.statistics_manager.get_statistics("users", "INSERT") == 1


def test_runtime_sequence_stops_after_rejected_constraint(manager):
    maintainer = RecordingMaintainer()
    manager.index_manager.create_index("users", Index("idx", "B_TREE", ["id"], maintainer=maintainer))
    manager.constraint_manager.create_constraint(
        "users", Constraint("positive_id", "CHECK", ["id"], RejectingEnforcer())
    )

    with pytest.raises(ValueError, match="rejected row"):
        manager.apply_table_event("users", "UPDATE", {"id": 0}, 1)

    assert maintainer.calls == []
    assert manager.metadata_manager.statistics_manager.get_statistics("users", "UPDATE") == 0

