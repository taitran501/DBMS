from dbms.storage_engine.log_file_manager import LogFileManager


def test_log_file_manager_can_be_created():
    assert isinstance(LogFileManager(), LogFileManager)
