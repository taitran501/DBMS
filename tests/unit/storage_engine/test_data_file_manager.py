from dbms.storage_engine.data_file_manager import DataFileManager


def test_data_file_manager_can_be_created():
    assert isinstance(DataFileManager(), DataFileManager)
