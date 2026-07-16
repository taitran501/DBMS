from dbms.storage_engine.buffer_pool import BufferPool
from dbms.storage_engine.page import Page


def test_buffer_pool_stores_capacity_and_returns_placeholders():
    pool = BufferPool(16)

    assert pool.capacity == 16
    assert pool.get_page(1) is None
    assert pool.put_page(Page(1)) is True
    assert pool.flush() is True
