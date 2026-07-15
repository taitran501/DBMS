import pytest

from dbms.database_object.constraint_management import Constraint
from dbms.database_object.index_management import Index
from dbms.database_object.metadata_management import Catalog
from dbms.database_object.relationship_management import Relationship, ReferentialActionPolicy
from dbms.database_object.schema_management.schema import ColumnSchema, TableSchema
from dbms.errors import ConstraintViolationError, ProcedureNotExecutableError
from dbms.subsystems import DatabaseObjectManager


@pytest.fixture
def db():
    from dbms.database_object.index_management import IndexManager
    manager = DatabaseObjectManager(Catalog(), IndexManager())
    manager.provision_table("public", "users", TableSchema("users", [
        ColumnSchema("id", "INT", nullable=False),
        ColumnSchema("name", "TEXT", default_value="anonymous"),
        ColumnSchema("active", "BOOLEAN", default_value=True),
    ]))
    manager.constraint_manager.create_constraint("users", Constraint("pk_users", "PRIMARY_KEY", ["id"]))
    manager.index_manager.create_index("users", Index("idx_users_id", "HASH", ["id"], unique=True))
    return manager


def test_insert_row_applies_defaults_converts_values_and_updates_indexes_and_statistics(db):
    """
    Test insertion with default values, type conversion, and ensure indexes
    and metadata statistics are correctly updated.
    """
    row_id = db.insert_row("public.users", {"id": "1"})
    assert row_id == 1
    assert db.select_rows("users") == ({"id": 1, "name": "anonymous", "active": True, "_row_id": 1},)
    assert db.index_manager.find_indexed_row_ids("users", "idx_users_id", (1,)) == (1,)
    assert db.metadata_manager.statistics_manager.get_statistics("users", "row_count") == 1


def test_unique_failure_is_atomic_and_ids_are_not_reused(db):
    """
    Ensure that a failed UNIQUE constraint validation correctly rolls back
    and atomicity is maintained without reusing sequential internal row IDs.
    """
    assert db.insert_row("users", {"id": 1}) == 1
    with pytest.raises(ConstraintViolationError):
        db.insert_row("users", {"id": 1})
    assert db.insert_row("users", {"id": 2}) == 2
    assert len(db.select_rows("users")) == 2


def test_update_delete_and_trigger_failure_roll_back(db):
    """
    Verify that an exception raised by an AFTER DELETE trigger prevents
    the deletion (rollback), while successful updates and deletes persist.
    """
    row_id = db.insert_row("users", {"id": 1, "name": "old"})
    assert db.update_row("users", row_id, {"name": "new"})["name"] == "new"
    db.provision_trigger("users", "reject-delete", "DELETE", "AFTER", lambda ctx: (_ for _ in ()).throw(RuntimeError("stop")))
    with pytest.raises(RuntimeError, match="stop"):
        db.delete_row("users", row_id)
    assert db.select_rows("users")[0]["name"] == "new"
    db.trigger_manager.drop_trigger("users", "reject-delete")
    assert db.delete_row("users", row_id)["id"] == 1
    assert db.select_rows("users") == ()


def test_insert_child_rejects_missing_parent_and_accepts_existing_parent(db):
    """
    Test that inserting a child row with a non-existent parent foreign key
    raises a ValueError, while inserting with a valid parent succeeds.
    """
    db.provision_table("public", "orders", TableSchema("orders", [ColumnSchema("user_id", "INT")]))
    db.relationship_manager.create_relationship(Relationship(
        "fk_orders_users", "orders", "users", "MANY_TO_ONE",
        ReferentialActionPolicy(), ("user_id",), ("id",),
    ))
    with pytest.raises(ValueError, match="Relationship"):
        db.insert_row("orders", {"user_id": 9})
    db.insert_row("users", {"id": 9})
    assert db.insert_row("orders", {"user_id": 9}) == 1


def test_delete_parent_cascades_to_dependent_rows(db):
    """
    Validate the CASCADE referential action policy on DELETE operations,
    ensuring child records are removed when their parent is deleted.
    """
    db.provision_table("public", "orders", TableSchema("orders", [ColumnSchema("user_id", "INT", nullable=True)]))
    db.relationship_manager.create_relationship(Relationship(
        "fk_orders_users", "orders", "users", "MANY_TO_ONE",
        ReferentialActionPolicy(on_delete="CASCADE"), ("user_id",), ("id",),
    ))
    user_id = db.insert_row("users", {"id": 7})
    db.insert_row("orders", {"user_id": 7})
    db.delete_row("users", user_id)
    assert db.select_rows("orders") == ()


def test_delete_parent_rejects_no_action_then_sets_dependent_key_to_null(db):
    """
    Validate NO ACTION (preventing deletion if dependents exist) and
    SET NULL referential action policies on DELETE operations.
    """
    db.provision_table("public", "orders", TableSchema("orders", [ColumnSchema("user_id", "INT", nullable=True)]))
    rel = Relationship("fk", "orders", "users", "MANY_TO_ONE", ReferentialActionPolicy(), ("user_id",), ("id",))
    db.relationship_manager.create_relationship(rel)
    user_id = db.insert_row("users", {"id": 8}); db.insert_row("orders", {"user_id": 8})
    with pytest.raises(ValueError, match="prevents delete"): db.delete_row("users", user_id)
    db.relationship_manager.relationships["fk"] = Relationship(
        "fk", "orders", "users", "MANY_TO_ONE", ReferentialActionPolicy(on_delete="SET_NULL"), ("user_id",), ("id",)
    )
    db.delete_row("users", user_id)
    assert db.select_rows("orders")[0]["user_id"] is None


def test_execute_procedure_runs_callable_and_rejects_non_executable_body(db):
    """
    Test execution of stored procedures and ensure that procedures defined
    with raw SQL instead of a Python callable raise ProcedureNotExecutableError.
    """
    db.provision_procedure("public", "sum", ["a", "b"], lambda a, b: a + b)
    assert db.stored_procedure_manager.execute_procedure("public", "sum", [2, 3]) == 5
    db.provision_procedure("public", "sql_only", [], "SELECT 1")
    with pytest.raises(ProcedureNotExecutableError):
        db.stored_procedure_manager.execute_procedure("public", "sql_only", [])
