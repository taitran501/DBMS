from dbms.storage_engine.storage_engine import StorageEngine


def test_storage_engine_can_be_created():
    assert isinstance(StorageEngine(), StorageEngine)
