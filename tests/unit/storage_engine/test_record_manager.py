from dbms.storage_engine.record_manager import RecordManager


def test_record_manager_can_be_created():
    assert isinstance(RecordManager(), RecordManager)
