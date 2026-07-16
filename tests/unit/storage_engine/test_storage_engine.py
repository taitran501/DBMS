from dbms.storage_engine.buffer_pool import BufferPool
from dbms.storage_engine.storage_engine import StorageEngine


def test_storage_engine_stores_buffer_pool_and_returns_placeholders():
    pool = BufferPool(16)
    engine = StorageEngine(pool)

    assert engine.buffer_pool is pool
    assert engine.read(1) is None
    assert engine.write(object()) is True
    assert engine.delete(1) is True
    assert engine.revert(1) is True
