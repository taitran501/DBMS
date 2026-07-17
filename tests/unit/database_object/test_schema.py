from dbms.database_object.schema import Schema


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
    pass


def test_drop_table():
    pass
