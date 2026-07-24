import pytest

from dbms.storage_engine.buffer_pool import BufferPool


@pytest.fixture(autouse=True)
def reset_buffer_pool_singleton():
    """Keep Storage Engine tests independent from the process-wide buffer pool."""
    BufferPool.reset_instance()
    yield
    BufferPool.reset_instance()
