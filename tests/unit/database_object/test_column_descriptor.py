from dbms.database_object.column_descriptor import ColumnDescriptor


def test_column_descriptor_stores_column_definition():
    descriptor = ColumnDescriptor("id", "INTEGER", nullable=False)

    assert descriptor.name == "id"
    assert descriptor.data_type == "INTEGER"
    assert descriptor.nullable is False
