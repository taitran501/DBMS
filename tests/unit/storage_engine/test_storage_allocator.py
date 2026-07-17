from dbms.storage_engine.storage_allocator import StorageAllocator

def test_allocate_storage_space():
    pass

def test_release_storage_space():
    pass

def test_reallocate_space():
    pass

def test_track_allocator_free_space():
    pass

def test_reject_exhausted_storage():
    pass

def test_reject_double_release():
    pass

def test_storage_allocator_can_be_created():
    assert isinstance(StorageAllocator(), StorageAllocator)
