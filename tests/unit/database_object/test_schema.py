from dbms.database_object.schema import Schema
from dbms.database_object.table import Table
from dbms.database_object.view import View
from dbms.database_object.stored_procedure import StoredProcedure


def test_schema_can_be_created():
    tables = {}
    schema = Schema("s1", "public", "admin", tables)

    assert schema.schema_id == "s1"
    assert schema.name == "public"
    assert schema.owner == "admin"
    assert schema.tables is tables
    assert callable(schema.create_table)
    assert callable(schema.drop_table)


def test_create_table():
    schema = Schema("s1", "public", "admin", {})
    table = Table("t1", "users")

    result = schema.create_table(table)

    assert result is True
    assert schema.tables["users"] is table


def test_get_table():
    table = Table("t1", "users")
    schema = Schema("s1", "public", "admin", {"users": table})

    result = schema.get_table("users")

    assert result is table


def test_rename_table():
    table = Table("t1", "users")
    schema = Schema("s1", "public", "admin", {"users": table})

    result = schema.rename_table("users", "customers")

    assert result is True
    assert table.name == "customers"
    assert schema.tables["customers"] is table
    assert "users" not in schema.tables


def test_drop_table():
    table = Table("t1", "users")
    schema = Schema("s1", "public", "admin", {"users": table})

    result = schema.drop_table("users")

    assert result is True
    assert "users" not in schema.tables


def test_create_view():
    schema = Schema("s1", "public", "admin")
    view = View("v1", "active_users", "SELECT * FROM users", object(), [])

    result = schema.create_view(view)

    assert result is True
    assert schema.views["active_users"] is view


def test_get_view():
    view = View("v1", "active_users", "SELECT * FROM users", object(), [])
    schema = Schema("s1", "public", "admin", views={"active_users": view})

    result = schema.get_view("active_users")

    assert result is view


def test_drop_view():
    view = View("v1", "active_users", "SELECT * FROM users", object(), [])
    schema = Schema("s1", "public", "admin", views={"active_users": view})

    result = schema.drop_view("active_users")

    assert result is True
    assert "active_users" not in schema.views


def test_create_stored_procedure():
    schema = Schema("s1", "public", "admin")
    procedure = StoredProcedure("p1", "calculate_total", object(), object())

    result = schema.create_stored_procedure(procedure)

    assert result is True
    assert schema.stored_procedures["calculate_total"] is procedure


def test_get_stored_procedure():
    procedure = StoredProcedure("p1", "calculate_total", object(), object())
    schema = Schema(
        "s1", "public", "admin",
        stored_procedures={"calculate_total": procedure},
    )

    result = schema.get_stored_procedure("calculate_total")

    assert result is procedure


def test_drop_stored_procedure():
    procedure = StoredProcedure("p1", "calculate_total", object(), object())
    schema = Schema(
        "s1", "public", "admin",
        stored_procedures={"calculate_total": procedure},
    )

    result = schema.drop_stored_procedure("calculate_total")

    assert result is True
    assert "calculate_total" not in schema.stored_procedures
