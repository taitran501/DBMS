from dbms.database_object.schema_manager import SchemaManager


def test_schema_manager_can_be_created():
    assert isinstance(SchemaManager(), SchemaManager)
