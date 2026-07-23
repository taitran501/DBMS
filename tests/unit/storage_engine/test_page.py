import pytest

from dbms.storage_engine.page import Page


def test_page_can_be_created():
    page = Page(1, b"initial_data")

    assert page.page_id == 1
    assert page.data == b"initial_data"
    assert callable(page.read_tuple)
    assert callable(page.insert_tuple)
    assert callable(page.write_tuple)
    assert callable(page.delete_tuple)


def test_read_and_write_tuple_at_a_specific_slot():
    page = Page(1)

    assert page.write_tuple(10, b"tuple_data") is True
    assert page.read_tuple(10) == b"tuple_data"


def test_insert_tuple_assigns_next_available_slot():
    page = Page(1)

    first_slot = page.insert_tuple(b"first")
    second_slot = page.insert_tuple(b"second")

    assert first_slot == 0
    assert second_slot == 1
    assert page.read_tuple(second_slot) == b"second"


def test_delete_tuple_releases_its_page_space():
    page = Page(1)
    slot_id = page.insert_tuple(b"tuple_data")

    assert page.delete_tuple(slot_id) is True
    assert page.read_tuple(slot_id) is None
    assert page.free_space == Page.PAGE_SIZE


def test_reject_tuple_larger_than_page_capacity():
    page = Page(1)

    with pytest.raises(ValueError, match="size"):
        page.insert_tuple(b"x" * (Page.PAGE_SIZE + 1))
