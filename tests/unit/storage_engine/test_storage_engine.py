from dbms.storage_engine.buffer_pool import BufferPool
from dbms.storage_engine.storage_engine import StorageEngine


def test_storage_engine_can_be_created():
    pass


def test_initialize():
    pass


def test_read_page():
    pass


def test_write_page():
    pass


def test_storage_engine_stores_buffer_pool():
    pool = BufferPool(16)
    engine = StorageEngine(pool)

    assert engine.buffer_pool is pool
