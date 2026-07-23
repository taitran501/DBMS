import pytest

from dbms.storage_engine.page_manager import PageManager


def test_page_manager_can_be_created():
    manager = PageManager()

    assert manager.pages == {}
    assert callable(manager.allocate_page)
    assert callable(manager.get_page)
    assert callable(manager.release_page)
    assert callable(manager.get_page_with_free_space)


def test_allocate_page_creates_the_first_page():
    manager = PageManager()

    page_id = manager.allocate_page()

    assert page_id == 1
    assert manager.get_page(page_id).page_id == page_id


def test_release_page_keeps_the_page_available_when_not_deallocated():
    manager = PageManager()
    page_id = manager.allocate_page()

    assert manager.release_page(page_id) is True
    assert manager.get_page(page_id) is not None


def test_deallocated_page_id_is_reused():
    manager = PageManager()
    page_id = manager.allocate_page()

    assert manager.release_page(page_id, deallocate=True) is True
    assert manager.allocate_page() == page_id


def test_track_page_free_space_uses_page_slots():
    manager = PageManager()
    page_id = manager.allocate_page()
    manager.get_page(page_id).insert_tuple(b"x" * 1024)

    assert manager.track_page_free_space(page_id) == 3072


def test_reject_request_larger_than_a_page():
    manager = PageManager()

    with pytest.raises(ValueError, match="size"):
        manager.get_page_with_free_space(required_bytes=4097)
