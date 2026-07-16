from dbms.storage_engine.buffer_pool import BufferPool


def test_buffer_pool_can_be_created():
    assert isinstance(BufferPool(), BufferPool)
