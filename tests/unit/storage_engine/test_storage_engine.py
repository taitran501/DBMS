from unittest.mock import Mock

import pytest

from dbms.storage_engine.buffer_pool import BufferPool
from dbms.storage_engine.exceptions import StorageEngineNotInitializedError
from dbms.storage_engine.page import Page
from dbms.storage_engine.storage_engine import StorageEngine


def test_storage_engine_can_be_created():
    """Ensure StorageEngine initializes with a given BufferPool instance."""
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
    """Ensure StorageEngine sets is_initialized to True upon calling initialize()."""
    # Arrange
    engine = StorageEngine(BufferPool(16))

    # Act
    result = engine.initialize()

    # Assert
    assert result is True
    assert engine.is_initialized is True


def test_read_page():
    """Ensure StorageEngine pins and returns page from buffer pool when initialized."""
    # Arrange
    page = Page(1)
    buffer_pool = Mock(spec=BufferPool)
    buffer_pool.pin_page.return_value = page
    engine = StorageEngine(buffer_pool)
    engine.initialize()

    # Act
    result = engine.read_page(1)

    # Assert
    assert result is page
    buffer_pool.pin_page.assert_called_once_with(1)


def test_write_page():
    """Ensure StorageEngine caches page into buffer pool when initialized."""
    # Arrange
    page = Page(1)
    buffer_pool = Mock(spec=BufferPool)
    buffer_pool.cache_page.return_value = True
    engine = StorageEngine(buffer_pool)
    engine.initialize()

    # Act
    result = engine.write_page(page)

    # Assert
    assert result is True
    buffer_pool.cache_page.assert_called_once_with(page)


def test_read_before_initialize():
    """Ensure attempting to read a page before initializing StorageEngine

    raises StorageEngineNotInitializedError to prevent accessing uninitialized storage.
    """
    # Arrange: Setup uninitialized engine
    buffer_pool = Mock(spec=BufferPool)
    engine = StorageEngine(buffer_pool)

    # Act & Assert: Reading page before initialize must raise StorageEngineNotInitializedError
    with pytest.raises(StorageEngineNotInitializedError):
        engine.read_page(1)

    buffer_pool.pin_page.assert_not_called()


def test_write_before_initialize():
    """Ensure attempting to write a page before initializing StorageEngine

    raises StorageEngineNotInitializedError to prevent corrupting uninitialized storage.
    """
    # Arrange: Setup uninitialized engine
    buffer_pool = Mock(spec=BufferPool)
    engine = StorageEngine(buffer_pool)

    # Act & Assert: Writing page before initialize must raise StorageEngineNotInitializedError
    with pytest.raises(StorageEngineNotInitializedError):
        engine.write_page(Page(1))

    buffer_pool.cache_page.assert_not_called()
