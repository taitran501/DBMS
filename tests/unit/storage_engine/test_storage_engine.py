from unittest.mock import Mock

from dbms.storage_engine.buffer_pool import BufferPool
from dbms.storage_engine.page import Page
from dbms.storage_engine.storage_engine import StorageEngine


def test_storage_engine_can_be_created():
    # Arrange
    buffer_pool = BufferPool(16)

    # Act
    engine = StorageEngine(buffer_pool)

    # Assert
    assert engine.buffer_pool is buffer_pool
    assert callable(engine.initialize)
    assert callable(engine.read_page)
    assert callable(engine.write_page)


def test_initialize():
    # Arrange
    engine = StorageEngine(BufferPool(16))

    # Act
    result = engine.initialize()

    # Assert
    assert result is True
    assert engine.is_initialized is True


def test_read_page():
    # Arrange
    page = Page(1)
    buffer_pool = Mock(spec=BufferPool)
    buffer_pool.pin_page.return_value = page
    engine = StorageEngine(buffer_pool)

    # Act
    result = engine.read_page(1)

    # Assert
    assert result is page
    buffer_pool.pin_page.assert_called_once_with(1)


def test_write_page():
    # Arrange
    page = Page(1)
    buffer_pool = Mock(spec=BufferPool)
    buffer_pool.cache_page.return_value = True
    engine = StorageEngine(buffer_pool)

    # Act
    result = engine.write_page(page)

    # Assert
    assert result is True
    buffer_pool.cache_page.assert_called_once_with(page)
