import pytest

from dbms.database_object.column_management import ColumnManager
from dbms.database_object.column_management.column_manager import Column
from dbms.database_object.metadata_management import DependencyManager, MetadataManager
from dbms.database_object.stored_procedure import ProcedureDescriptor, ProcedureExecutor


def test_get_column_rejects_missing_column_in_existing_table():
    manager = ColumnManager()
    manager.add_column("users", Column("id", "INT"))

    with pytest.raises(ValueError, match="Column email not found in table users"):
        manager.get_column("users", "email")


def test_get_column_rejects_lookup_in_existing_empty_table():
    manager = ColumnManager()
    manager.columns["users"] = []

    with pytest.raises(ValueError, match="Column id not found in table users"):
        manager.get_column("users", "id")


def test_get_column_rejects_lookup_in_missing_table():
    manager = ColumnManager()

    with pytest.raises(ValueError, match="Column id not found in table missing"):
        manager.get_column("missing", "id")


def test_recursive_dependencies_are_unique_for_cycles_and_converging_paths():
    dependencies = DependencyManager()
    dependencies.add_metadata_dependency("view:a", "table:t")
    dependencies.add_metadata_dependency("view:b", "table:t")
    dependencies.add_metadata_dependency("trigger:c", "view:a")
    dependencies.add_metadata_dependency("trigger:c", "view:b")
    dependencies.add_metadata_dependency("view:a", "trigger:c")

    assert dependencies.get_metadata_dependents("table:t", recursive=True) == (
        "view:a",
        "view:b",
        "trigger:c",
    )


def test_metadata_register_accepts_omitted_dependencies():
    metadata = MetadataManager()
    descriptor = object()

    metadata.register_metadata("table", "users", descriptor)

    assert metadata.get_metadata("table", "users") is descriptor
    assert metadata.dependency_manager.get_metadata_dependencies("table:users") == ()


def test_metadata_register_accepts_explicit_empty_dependencies():
    metadata = MetadataManager()

    metadata.register_metadata("table", "users", object(), dependencies=[])

    assert metadata.dependency_manager.get_metadata_dependencies("table:users") == ()


def test_metadata_update_replaces_registered_descriptor():
    metadata = MetadataManager()
    metadata.register_metadata("table", "users", object())
    replacement = object()

    metadata.update_metadata("table", "users", replacement)

    assert metadata.get_metadata("table", "users") is replacement


def test_callable_procedure_rejects_wrong_argument_count():
    executor = ProcedureExecutor()
    procedure = ProcedureDescriptor("add", ["a", "b"], lambda a, b: a + b)

    with pytest.raises(ValueError, match="Procedure add expects 2 arguments"):
        executor.execute_procedure_body(procedure, [1])
