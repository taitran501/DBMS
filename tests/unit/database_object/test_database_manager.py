from unittest.mock import Mock
import pytest

from dbms.database_object.database import Database
from dbms.database_object.database_manager import DatabaseManager
from dbms.database_object.exceptions import DatabaseInUseError, DuplicateDatabaseError, UnknownDatabaseError


def create_database(name="test_db", status="closed"):
    db = Mock(spec=Database, name=name)
    db.status = status
    return db


def test_database_manager_can_be_created():
    # Arrange
    database_factory = object()
    storage = object()
    databases = {}
    manager = DatabaseManager(database_factory, storage, databases)

    # Assert
    assert manager.database_factory is database_factory
    assert manager.storage is storage
    assert manager.databases is databases
    assert callable(manager.create_database)
    assert callable(manager.get_database)
    assert callable(manager.rename_database)
    assert callable(manager.drop_database)


def test_create_database():
    # Arrange
    database = create_database()
    database_factory = Mock()
    database_factory.create.return_value = database
    manager = DatabaseManager(database_factory, Mock(), {})

    # Act
    result = manager.create_database("test_db")

    # Assert
    assert result is database
    assert manager.databases["test_db"] is database
    database_factory.create.assert_called_once_with("test_db")


def test_get_database():
    # Arrange
    database = create_database()
    manager = DatabaseManager(Mock(), Mock(), {"test_db": database})

    # Act
    result = manager.get_database("test_db")

    # Assert
    assert result is database


def test_rename_database():
    # Arrange
    database = create_database()
    manager = DatabaseManager(Mock(), Mock(), {"test_db": database})

    # Act
    result = manager.rename_database("test_db", "renamed_db")

    # Assert
    assert result is True
    assert database.name == "renamed_db"
    assert manager.databases["renamed_db"] is database
    assert "test_db" not in manager.databases


def test_drop_database():
    # Arrange
    database = create_database()
    storage = Mock()
    manager = DatabaseManager(Mock(), storage, {"test_db": database})

    # Act
    result = manager.drop_database("test_db")

    # Assert
    assert result is True
    assert "test_db" not in manager.databases
    storage.delete_database_files.assert_called_once_with("test_db")


def test_reject_duplicate_database():
    # Arrange
    existing_db = create_database("test_db")
    manager = DatabaseManager(Mock(), Mock(), {"test_db": existing_db})

    # Act & Assert
    with pytest.raises(DuplicateDatabaseError):
        manager.create_database("test_db")


def test_get_unknown_database():
    # Arrange
    manager = DatabaseManager(Mock(), Mock(), {})

    # Act & Assert
    with pytest.raises(UnknownDatabaseError):
        manager.get_database("non_existent_db")


def test_drop_unknown_database():
    # Arrange
    manager = DatabaseManager(Mock(), Mock(), {})

    # Act & Assert
    with pytest.raises(UnknownDatabaseError):
        manager.drop_database("non_existent_db")


def test_rename_database_to_existing_name():
    # Arrange: Setup two existing databases (db1 and db2)
    db1 = create_database("db1")
    db2 = create_database("db2")
    manager = DatabaseManager(Mock(), Mock(), {"db1": db1, "db2": db2})

    # Act & Assert: Renaming db1 to existing db2 name should raise DuplicateDatabaseError
    with pytest.raises(DuplicateDatabaseError):
        manager.rename_database("db1", "db2")


def test_rename_unknown_database_raises_exception():
    # Arrange: Setup manager with no databases
    manager = DatabaseManager(Mock(), Mock(), {})

    # Act & Assert: Renaming a non-existent database should raise UnknownDatabaseError
    with pytest.raises(UnknownDatabaseError):
        manager.rename_database("non_existent_db", "new_name")


def test_create_database_invalid_name_raises_value_error():
    # Arrange: Setup manager with valid factory
    manager = DatabaseManager(Mock(), Mock(), {})

    # Act & Assert: Creating database with empty string name should raise ValueError
    with pytest.raises(ValueError):
        manager.create_database("")


def test_drop_open_database_raises_database_in_use_error():
    # Arrange: Database is currently active/open
    open_db = create_database("active_db", status="open")
    manager = DatabaseManager(Mock(), Mock(), {"active_db": open_db})

    # Act & Assert: An open database cannot be dropped until it is closed
    with pytest.raises(DatabaseInUseError):
        manager.drop_database("active_db")
