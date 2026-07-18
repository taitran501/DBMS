import pytest
from unittest.mock import Mock

from dbms.storage_engine.buffer_pool import BufferPool
from dbms.storage_engine.page import Page
from dbms.storage_engine.page_manager import PageManager


def test_page_manager_can_be_created():
    # Arrange
    buffer_pool = Mock(spec=BufferPool)

    # Act
    manager = PageManager(buffer_pool)

    # Assert
    assert manager.buffer_pool is buffer_pool
    assert callable(manager.allocate_page)
    assert callable(manager.get_page)
    assert callable(manager.release_page)
    assert callable(manager.get_page_with_free_space)


def test_allocate_page():
    # Arrange
    manager = PageManager(Mock(spec=BufferPool))

    # Act
    page_id = manager.allocate_page()

    # Assert
    assert page_id == 1


def test_get_page():
    # Arrange
    page = Page(2)
    buffer_pool = Mock(spec=BufferPool)
    buffer_pool.pin_page.return_value = page
    manager = PageManager(buffer_pool)

    # Act
    result = manager.get_page(2)

    # Assert
    assert result is page
    buffer_pool.pin_page.assert_called_once_with(2)


def test_release_page():
    # Arrange
    buffer_pool = Mock()
    buffer_pool.unpin_page.return_value = True
    manager = PageManager(buffer_pool)

    # Act
    result = manager.release_page(2)

    # Assert
    assert result is True
    buffer_pool.unpin_page.assert_called_once_with(2)


def test_reuse_page():
    # Arrange
    buffer_pool = Mock()
    buffer_pool.unpin_page.return_value = True
    manager = PageManager(buffer_pool)

    # Act
    released = manager.release_page(2, deallocate=True)
    reused_page_id = manager.allocate_page()

    # Assert
    assert released is True
    assert reused_page_id == 2


def test_track_page_free_space():
    # Arrange
    manager = PageManager(Mock(spec=BufferPool))
    manager.page_free_space[2] = 1024

    # Act
    result = manager.track_page_free_space(2)

    # Assert
    assert result == 1024


def test_reject_full_page():
    # Arrange
    manager = PageManager(Mock(spec=BufferPool))
    manager.page_free_space = {1: 1024}

    # Act / Assert
    with pytest.raises(Exception, match="space"):
        manager.get_page_with_free_space(required_bytes=2048)
