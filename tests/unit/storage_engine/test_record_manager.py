from unittest.mock import Mock

import pytest

from dbms.database_object.row import Row
from dbms.storage_engine.exceptions import RecordNotFoundError
from dbms.storage_engine.page_manager import PageManager
from dbms.storage_engine.record_manager import RecordManager


def test_record_manager_can_be_created():
    page_manager = PageManager()

    manager = RecordManager(page_manager)

    assert manager.page_manager is page_manager
    assert callable(manager.read_row)
    assert callable(manager.insert_row)
    assert callable(manager.update_row)
    assert callable(manager.delete_row)


def test_insert_and_read_row():
    manager = RecordManager(PageManager())
    row = Row("customer-1", {"name": "Ada"}, "v1")

    location = manager.insert_row(row)

    assert location == "1:0"
    assert manager.read_row(location).values == {"name": "Ada"}


def test_update_row_overwrites_the_same_slot():
    manager = RecordManager(PageManager())
    location = manager.insert_row(Row("customer-1", {"name": "Ada"}, "v1"))

    assert manager.update_row(location, Row("customer-1", {"name": "Grace"}, "v2"))
    assert manager.read_row(location).values == {"name": "Grace"}


def test_delete_row_removes_its_slot():
    manager = RecordManager(PageManager())
    location = manager.insert_row(Row("customer-1", {"name": "Ada"}, "v1"))

    assert manager.delete_row(location) is True
    with pytest.raises(RecordNotFoundError):
        manager.read_row(location)


def test_read_unknown_row_raises_record_not_found():
    manager = RecordManager(PageManager())

    with pytest.raises(RecordNotFoundError):
        manager.read_row("1:2")


def test_update_unknown_row_raises_record_not_found():
    manager = RecordManager(PageManager())

    with pytest.raises(RecordNotFoundError):
        manager.update_row("1:2", Row("customer-1", {"name": "Ada"}, "v1"))


def test_delete_unknown_row_raises_record_not_found():
    manager = RecordManager(PageManager())

    with pytest.raises(RecordNotFoundError):
        manager.delete_row("1:2")


def test_operations_release_the_page_after_use():
    page_manager = Mock(wraps=PageManager())
    manager = RecordManager(page_manager)
    location = manager.insert_row(Row("customer-1", {"name": "Ada"}, "v1"))

    manager.read_row(location)

    assert page_manager.release_page.call_count == 2
    page_manager.release_page.assert_called_with(1)
