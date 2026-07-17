from dbms.storage_engine.buffer_pool import BufferPool


def test_buffer_pool_can_be_created():
    pass


def test_pin_page():
    pass

def test_cache_page():
    pass

def test_get_cached_page():
    pass

def test_load_missing_page():
    pass

def test_enforce_capacity():
    pass

def test_evict_page():
    pass

def test_preserve_pinned_page():
    pass

def test_mark_dirty():
    pass

def test_flush_page():
    pass

def test_flush_all_pages():
    pass

def test_buffer_pool_stores_capacity_and_returns_placeholders():
    pool = BufferPool(10)
    assert pool.capacity == 10
    assert pool.get_page(1) is None
    assert pool.flush() is True
