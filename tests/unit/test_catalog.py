import pytest
from dbms.database_object.metadata_management.system_catalog import Catalog
from dbms.database_object.schema_management.schema import TableSchema, ColumnSchema
from dbms.errors import TableAlreadyExistsError, TableNotFoundError, ColumnNotFoundError

def test_create_and_get_table():
    catalog = Catalog()

    schema = TableSchema(
        name="users",
        columns=[
            ColumnSchema("id", "INT"),
            ColumnSchema("name", "TEXT"),
        ],
    )

    catalog.create_table(schema)

    assert catalog.has_table("users") is True
    assert catalog.get_table("users").column_names() == ["id", "name"]

def test_create_duplicate_table():
    catalog = Catalog()
    schema = TableSchema("users", [])
    catalog.create_table(schema)

    with pytest.raises(TableAlreadyExistsError):
        catalog.create_table(schema)

def test_get_nonexistent_table():
    catalog = Catalog()
    with pytest.raises(TableNotFoundError):
        catalog.get_table("users")

def test_get_column_schema():
    schema = TableSchema("users", [ColumnSchema("id", "INT")])
    col = schema.get_column("id")
    assert col.name == "id"
    assert col.data_type == "INT"

    with pytest.raises(ColumnNotFoundError):
        schema.get_column("invalid")
