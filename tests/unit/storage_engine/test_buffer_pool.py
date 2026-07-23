from unittest.mock import Mock

import pytest

from dbms.storage_engine.buffer_pool import BufferPool
from dbms.storage_engine.buffer_replacement_strategy import LruReplacementStrategy
from dbms.storage_engine.exceptions import BufferPoolFullError
from dbms.storage_engine.file_manager import FileManager
from dbms.storage_engine.page import Page


def test_buffer_pool_can_be_created():
    # Arrange
    capacity = 10
    page_store = Mock()

    # Act
    pool = BufferPool(capacity, page_store)

    # Assert
    assert pool.capacity == capacity
    assert pool.page_store is page_store
    assert callable(pool.pin_page)
    assert callable(pool.cache_page)
    assert callable(pool.get_cached_page)
    assert callable(pool.evict_page)
    assert callable(pool.mark_dirty)
    assert callable(pool.flush_page)
    assert callable(pool.flush_all_pages)


def test_pin_page():
    # Arrange
    page = Page(1)
    pool = BufferPool(10, Mock())
    pool.cache_page(page)

    # Act
    result = pool.pin_page(1)

    # Assert
    assert result is page
    assert pool.pin_counts[1] == 1


def test_unpin_page():
    # Arrange
    page = Page(1)
    pool = BufferPool(10, Mock())
    pool.cache_page(page)
    # Pinning protects the page from eviction until its pin count returns to zero.
    pool.pin_page(1)

    # Act
    result = pool.unpin_page(1)

    # Assert
    assert result is True
    assert pool.pin_counts[1] == 0


def test_cache_page():
    # Arrange
    page = Page(1)
    pool = BufferPool(10, Mock())

    # Act
    result = pool.cache_page(page)

    # Assert
    assert result is True
    assert pool.get_cached_page(1) is page


def test_get_cached_page():
    # Arrange
    page = Page(1)
    pool = BufferPool(10, Mock())
    pool.cache_page(page)

    # Act
    result = pool.get_cached_page(1)

    # Assert
    assert result is page


def test_load_missing_page():
    # Arrange
    page = Page(5)
    page_store = Mock()
    page_store.load_page.return_value = page
    pool = BufferPool(10, page_store)

    # Act
    result = pool.pin_page(5)

    # Assert
    assert result is page
    assert pool.get_cached_page(5) is page
    page_store.load_page.assert_called_once_with(5)


def test_pin_page_loads_from_the_configured_page_store(tmp_path):
    page_store = FileManager(str(tmp_path))
    stored_page = Page(5)
    stored_page.write_tuple(0, b"customer-row")
    page_store.write_page(stored_page)
    pool = BufferPool(10, page_store)

    page = pool.pin_page(5)

    assert page is not None
    assert page.read_tuple(0) == b"customer-row"
    assert pool.pin_counts[5] == 1


def test_enforce_capacity():
    # Arrange
    pool = BufferPool(1, Mock())
    first_page = Page(1)
    second_page = Page(2)
    pool.cache_page(first_page)

    # Act
    result = pool.cache_page(second_page)

    # Assert
    assert result is True
    assert pool.get_cached_page(2) is second_page
    assert len(pool.pages) == 1


def test_lru_strategy_changes_the_page_selected_for_eviction():
    pool = BufferPool(2, Mock(), LruReplacementStrategy())
    first_page = Page(1)
    second_page = Page(2)
    pool.cache_page(first_page)
    pool.cache_page(second_page)
    pool.pin_page(1)
    pool.unpin_page(1)

    assert pool.cache_page(Page(3)) is True
    assert pool.get_cached_page(1) is first_page
    assert pool.get_cached_page(2) is None
    assert pool.get_cached_page(3) is not None


def test_evict_page():
    # Arrange
    page = Page(1)
    page_store = Mock()
    page_store.write_page.return_value = True
    pool = BufferPool(10, page_store)
    pool.cache_page(page)
    pool.mark_dirty(1)

    # Act
    result = pool.evict_page()

    # Assert
    assert result is True
    assert pool.get_cached_page(1) is None
    page_store.write_page.assert_called_once_with(page)


def test_preserve_pinned_page():
    # Arrange
    pinned_page = Page(1)
    evictable_page = Page(2)
    pool = BufferPool(10, Mock())
    pool.cache_page(pinned_page)
    pool.cache_page(evictable_page)
    pool.pin_page(1)

    # Act
    result = pool.evict_page()

    # Assert
    assert result is True
    assert pool.get_cached_page(1) is pinned_page
    assert pool.get_cached_page(2) is None


def test_mark_dirty():
    # Arrange
    pool = BufferPool(10, Mock())
    pool.cache_page(Page(1))

    # Act
    result = pool.mark_dirty(1)

    # Assert
    assert result is True
    assert 1 in pool.dirty_page_ids


def test_flush_page():
    # Arrange
    page = Page(1)
    page_store = Mock()
    page_store.write_page.return_value = True
    pool = BufferPool(10, page_store)
    pool.cache_page(page)
    pool.mark_dirty(1)

    # Act
    result = pool.flush_page(1)

    # Assert
    assert result is True
    assert 1 not in pool.dirty_page_ids
    page_store.write_page.assert_called_once_with(page)


def test_flush_all_pages():
    # Arrange
    first_page = Page(1)
    second_page = Page(2)
    page_store = Mock()
    page_store.write_page.return_value = True
    pool = BufferPool(10, page_store)
    pool.cache_page(first_page)
    pool.cache_page(second_page)
    pool.mark_dirty(1)
    pool.mark_dirty(2)

    # Act
    result = pool.flush_all_pages()

    # Assert
    assert result is True
    assert pool.dirty_page_ids == set()
    page_store.write_page.assert_any_call(first_page)
    page_store.write_page.assert_any_call(second_page)


def test_buffer_pool_stores_capacity():
    # Arrange
    capacity = 10
    page_store = Mock()

    # Act
    pool = BufferPool(capacity, page_store)

    # Assert
    assert pool.capacity == capacity


def test_failed_flush_preserves_dirty_page():
    """Ensure that if flushing a dirty page to disk fails (disk I/O error),

    the buffer pool retains the page in RAM and keeps its dirty status.
    """
    # Arrange: Cache a page and mark it dirty while mimicking a disk write failure
    page = Page(1)
    page_store = Mock()
    page_store.write_page.return_value = False
    pool = BufferPool(10, page_store)
    pool.cache_page(page)
    pool.mark_dirty(1)

    # Act: Attempt to flush the dirty page to disk
    result = pool.flush_page(1)

    # Assert: Flush should fail, but page must remain in RAM and stay dirty for future retries
    assert result is False
    assert pool.get_cached_page(1) is page
    assert 1 in pool.dirty_page_ids


def test_failed_dirty_eviction_preserves_page():
    """Ensure that if evicting a dirty page fails during disk flush,

    the buffer pool preserves the page in memory instead of dropping it.
    """
    # Arrange: Setup pool with a dirty page and failing disk write
    page = Page(1)
    page_store = Mock()
    page_store.write_page.return_value = False
    pool = BufferPool(10, page_store)
    pool.cache_page(page)
    pool.mark_dirty(1)

    # Act: Attempt to evict the dirty page
    result = pool.evict_page()

    # Assert: Eviction should fail to prevent unwritten data loss
    assert result is False
    assert pool.get_cached_page(1) is page
    assert 1 in pool.dirty_page_ids


def test_reject_cache_when_all_pages_are_pinned():
    """Ensure that attempting to cache a new page when all existing pages

    are pinned raises BufferPoolFullError to prevent unpinning active pages.
    """
    # Arrange: Fill buffer pool to capacity with a pinned page
    pinned_page = Page(1)
    pool = BufferPool(1, Mock())
    pool.cache_page(pinned_page)
    pool.pin_page(1)

    # Act & Assert: Caching a new page should fail with BufferPoolFullError
    with pytest.raises(BufferPoolFullError):
        pool.cache_page(Page(2))

    assert pool.get_cached_page(1) is pinned_page
    assert pool.get_cached_page(2) is None
