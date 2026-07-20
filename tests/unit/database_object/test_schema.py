import pytest

from dbms.database_object.schema import Schema
from dbms.database_object.table import Table
from dbms.database_object.view import View
from dbms.database_object.stored_procedure import StoredProcedure


def test_schema_can_be_created():
    # Arrange
    tables = {}
    schema = Schema("s1", "public", "admin", tables)

    # Assert
    assert schema.schema_id == "s1"
    assert schema.name == "public"
    assert schema.owner == "admin"
    assert schema.tables is tables
    assert callable(schema.create_table)
    assert callable(schema.drop_table)


def test_create_table():
    # Arrange
    schema = Schema("s1", "public", "admin", {})
    table = Table("t1", "users")

    # Act
    result = schema.create_table(table)

    # Assert
    assert result is True
    assert schema.tables["users"] is table


def test_get_table():
    # Arrange
    table = Table("t1", "users")
    schema = Schema("s1", "public", "admin", {"users": table})

    # Act
    result = schema.get_table("users")

    # Assert
    assert result is table


def test_rename_table():
    # Arrange
    table = Table("t1", "users")
    schema = Schema("s1", "public", "admin", {"users": table})

    # Act
    result = schema.rename_table("users", "customers")

    # Assert
    assert result is True
    assert table.name == "customers"
    assert schema.tables["customers"] is table
    assert "users" not in schema.tables


def test_drop_table():
    # Arrange
    table = Table("t1", "users")
    schema = Schema("s1", "public", "admin", {"users": table})

    # Act
    result = schema.drop_table("users")

    # Assert
    assert result is True
    assert "users" not in schema.tables


def test_create_view():
    # Arrange
    schema = Schema("s1", "public", "admin")
    view = View("v1", "active_users", "SELECT * FROM users", object(), [])

    # Act
    result = schema.create_view(view)

    # Assert
    assert result is True
    assert schema.views["active_users"] is view


def test_get_view():
    # Arrange
    view = View("v1", "active_users", "SELECT * FROM users", object(), [])
    schema = Schema("s1", "public", "admin", views={"active_users": view})

    # Act
    result = schema.get_view("active_users")

    # Assert
    assert result is view


def test_drop_view():
    # Arrange
    view = View("v1", "active_users", "SELECT * FROM users", object(), [])
    schema = Schema("s1", "public", "admin", views={"active_users": view})

    # Act
    result = schema.drop_view("active_users")

    # Assert
    assert result is True
    assert "active_users" not in schema.views


def test_create_stored_procedure():
    # Arrange
    schema = Schema("s1", "public", "admin")
    procedure = StoredProcedure("p1", "calculate_total", object(), object())

    # Act
    result = schema.create_stored_procedure(procedure)

    # Assert
    assert result is True
    assert schema.stored_procedures["calculate_total"] is procedure


def test_get_stored_procedure():
    # Arrange
    procedure = StoredProcedure("p1", "calculate_total", object(), object())
    schema = Schema(
        "s1", "public", "admin",
        stored_procedures={"calculate_total": procedure},
    )

    # Act
    result = schema.get_stored_procedure("calculate_total")

    # Assert
    assert result is procedure


def test_drop_stored_procedure():
    # Arrange
    procedure = StoredProcedure("p1", "calculate_total", object(), object())
    schema = Schema(
        "s1", "public", "admin",
        stored_procedures={"calculate_total": procedure},
    )

    # Act
    result = schema.drop_stored_procedure("calculate_total")

    # Assert
    assert result is True
    assert "calculate_total" not in schema.stored_procedures


def test_reject_duplicate_table():
    # Arrange
    existing_table = Table("t1", "users")
    schema = Schema("s1", "public", "admin", tables={"users": existing_table})
    new_table = Table("t2", "users")

    # Act & Assert
    with pytest.raises(ValueError):
        schema.create_table(new_table)


def test_get_unknown_table():
    # Arrange
    schema = Schema("s1", "public", "admin", tables={})

    # Act & Assert
    with pytest.raises(KeyError):
        schema.get_table("non_existent_table")


def test_drop_unknown_table():
    # Arrange
    schema = Schema("s1", "public", "admin", tables={})

    # Act & Assert
    with pytest.raises(KeyError):
        schema.drop_table("non_existent_table")


def test_rename_table_to_existing_name():
    # Arrange
    t1 = Table("t1", "users")
    t2 = Table("t2", "customers")
    schema = Schema("s1", "public", "admin", tables={"users": t1, "customers": t2})

    # Act & Assert
    with pytest.raises(ValueError):
        schema.rename_table("users", "customers")
