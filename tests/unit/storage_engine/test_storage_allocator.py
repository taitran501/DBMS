from dbms.storage_engine.storage_allocator import StorageAllocator


def test_storage_allocator_can_be_created():
    assert isinstance(StorageAllocator(), StorageAllocator)
