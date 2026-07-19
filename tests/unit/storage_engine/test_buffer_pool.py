from unittest.mock import Mock

from dbms.storage_engine.buffer_pool import BufferPool
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
