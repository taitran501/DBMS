from dbms.database_object.database_manager import DatabaseManager
from dbms.database_object.database import Database
from unittest.mock import Mock


def create_database(name="test_db"):
    return Mock(spec=Database, name=name)


def test_database_manager_can_be_created():
    database_factory = object()
    storage = object()
    databases = {}
    manager = DatabaseManager(database_factory, storage, databases)

    assert manager.database_factory is database_factory
    assert manager.storage is storage
    assert manager.databases is databases
    assert callable(manager.create_database)
    assert callable(manager.get_database)
    assert callable(manager.rename_database)
    assert callable(manager.drop_database)


def test_create_database():
    database = create_database()
    database_factory = Mock()
    database_factory.create.return_value = database
    manager = DatabaseManager(database_factory, Mock(), {})

    result = manager.create_database("test_db")

    assert result is database
    assert manager.databases["test_db"] is database
    database_factory.create.assert_called_once_with("test_db")


def test_get_database():
    database = create_database()
    manager = DatabaseManager(Mock(), Mock(), {"test_db": database})

    result = manager.get_database("test_db")

    assert result is database


def test_rename_database():
    database = create_database()
    manager = DatabaseManager(Mock(), Mock(), {"test_db": database})

    result = manager.rename_database("test_db", "renamed_db")

    assert result is True
    assert database.name == "renamed_db"
    assert manager.databases["renamed_db"] is database
    assert "test_db" not in manager.databases


def test_drop_database():
    database = create_database()
    storage = Mock()
    manager = DatabaseManager(Mock(), storage, {"test_db": database})

    result = manager.drop_database("test_db")

    assert result is True
    assert "test_db" not in manager.databases
    storage.delete_database_files.assert_called_once_with("test_db")
