from dbms.database_object.data_type_manager import DataTypeManager


def test_data_type_manager_can_be_created():
    assert isinstance(DataTypeManager(), DataTypeManager)
