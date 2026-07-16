from dbms.database_object.table_descriptor import TableDescriptor


def test_table_descriptor_stores_table_identity():
    descriptor = TableDescriptor("users", "public")

    assert descriptor.name == "users"
    assert descriptor.schema_name == "public"
