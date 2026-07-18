import pytest
from unittest.mock import Mock

from dbms.storage_engine.page import Page
from dbms.storage_engine.page_manager import PageManager
from dbms.storage_engine.record import Record
from dbms.storage_engine.record_manager import RecordManager


def test_record_manager_can_be_created():
    # Arrange
    page_manager = Mock()

    # Act
    manager = RecordManager(page_manager)

    # Assert
    assert manager.page_manager is page_manager
    assert callable(manager.read_record)
    assert callable(manager.move_record)
    assert callable(manager.insert_record)
    assert callable(manager.update_record)
    assert callable(manager.delete_record)


def test_read_record():
    # Arrange
    record = Mock()
    record.serialize.return_value = b"serialized-record"
    page = Mock(spec=Page)
    page.read_tuple.return_value = record.serialize()
    page_manager = Mock()
    page_manager.get_page.return_value = page
    manager = RecordManager(page_manager)

    # Act
    result = manager.read_record("1:2")

    # Assert
    assert result.record_id == 1
    assert result.values == {"name": "Ada"}
    page_manager.get_page.assert_called_once_with(1)
    page.read_tuple.assert_called_once_with(2)


def test_move_record():
    # Arrange
    page_manager = Mock()
    manager = RecordManager(page_manager)
    manager.records = {"1:2": Record(1, {"name": "Ada"})}

    # Act
    result = manager.move_record("1:2", "3:4")

    # Assert
    assert result is True
    assert "1:2" not in manager.records
    assert manager.records["3:4"].values == {"name": "Ada"}


def test_insert_record():
    # Arrange
    record = Mock()
    record.serialize.return_value = b"serialized-record"
    page = Mock(spec=Page)
    page.page_id = 1
    page.write_tuple.return_value = 2
    page_manager = Mock()
    page_manager.get_page_with_free_space.return_value = page
    manager = RecordManager(page_manager)

    # Act
    result = manager.insert_record(record)

    # Assert
    assert result == "1:2"
    page_manager.get_page_with_free_space.assert_called_once()
    page.write_tuple.assert_called_once_with(record.serialize())


def test_update_record():
    # Arrange
    updated_record = Mock()
    updated_record.serialize.return_value = b"updated-record"
    page = Mock()
    page.write_tuple.return_value = True
    page_manager = Mock()
    page_manager.get_page.return_value = page
    manager = RecordManager(page_manager)

    # Act
    result = manager.update_record("1:2", updated_record)

    # Assert
    assert result is True
    page_manager.get_page.assert_called_once_with(1)
    page.write_tuple.assert_called_once_with(2, updated_record.serialize())


def test_delete_record():
    # Arrange
    page = Mock()
    page.delete_tuple.return_value = True
    page_manager = Mock()
    page_manager.get_page.return_value = page
    manager = RecordManager(page_manager)

    # Act
    result = manager.delete_record("1:2")

    # Assert
    assert result is True
    page_manager.get_page.assert_called_once_with(1)
    page.delete_tuple.assert_called_once_with(2)


def test_reject_oversized_record():
    # Arrange
    page_manager = Mock()
    manager = RecordManager(page_manager)
    oversized_record = Mock(spec=Record)
    oversized_record.serialize.return_value = b"x" * 4097

    # Act / Assert
    with pytest.raises(Exception, match="size"):
        manager.insert_record(oversized_record)
