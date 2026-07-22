from unittest.mock import Mock
import pytest

from dbms.database_object.database import Database
from dbms.database_object.schema import Schema
from dbms.database_object.exceptions import DuplicateSchemaError, UnknownSchemaError


def create_database(schemas=None):
    storage = Mock()
    backup_service = Mock()
    database = Database(
        "db1", "test_db", "admin", "closed", 4096, "utf-8",
        "/data", "public", storage, backup_service, schemas if schemas is not None else {},
    )
    return database, storage, backup_service


def test_database_can_be_created():
    # Arrange
    storage = object()
    backup_service = object()
    schemas = {}
    database = Database(
        "db1",
        "test_db",
        "admin",
        "active",
        4096,
        "utf-8",
        "/data",
        "public",
        storage,
        backup_service,
        schemas,
    )

    # Assert
    assert database.database_id == "db1"
    assert database.name == "test_db"
    assert database.owner == "admin"
    assert database.status == "active"
    assert database.page_size == 4096
    assert database.encoding == "utf-8"
    assert database.storage_location == "/data"
    assert database.default_schema == "public"
    assert database.storage is storage
    assert database.backup_service is backup_service
    assert database.schemas is schemas
    assert callable(database.open)
    assert callable(database.close)
    assert callable(database.backup)
    assert callable(database.restore)


def test_open():
    # Arrange
    database, storage, _ = create_database()
    schemas = {"public": Schema("s1", "public", "admin")}
    storage.load_schema_metadata.return_value = schemas

    # Act
    result = database.open()

    # Assert
    assert result is True
    assert database.status == "open"
    assert database.schemas is schemas
    storage.load_schema_metadata.assert_called_once_with(database)


def test_close():
    # Arrange
    database, storage, _ = create_database()

    # Act
    result = database.close()

    # Assert
    assert result is True
    assert database.status == "closed"
    storage.flush_dirty_pages.assert_called_once_with(database)


def test_backup():
    # Arrange
    database, _, backup_service = create_database()

    # Act
    result = database.backup()

    # Assert
    assert result is True
    backup_service.create_backup.assert_called_once_with(database)


def test_restore():
    # Arrange
    database, _, backup_service = create_database()

    # Act
    result = database.restore()

    # Assert
    assert result is True
    backup_service.restore_backup.assert_called_once_with(database)


def test_create_schema():
    # Arrange
    database, _, _ = create_database({})
    schema = Schema("s1", "public", "admin")

    # Act
    result = database.create_schema(schema)

    # Assert
    assert result is True
    assert database.schemas["public"] is schema


def test_get_schema():
    # Arrange
    schema = Schema("s1", "public", "admin")
    database, _, _ = create_database({"public": schema})

    # Act
    result = database.get_schema("public")

    # Assert
    assert result is schema


def test_rename_schema():
    # Arrange
    schema = Schema("s1", "public", "admin")
    database, _, _ = create_database({"public": schema})

    # Act
    result = database.rename_schema("public", "application")

    # Assert
    assert result is True
    assert schema.name == "application"
    assert database.schemas["application"] is schema
    assert "public" not in database.schemas


def test_drop_schema():
    # Arrange
    schema = Schema("s1", "application", "admin")
    database, _, _ = create_database({"application": schema})

    # Act
    result = database.drop_schema("application")

    # Assert
    assert result is True
    assert "application" not in database.schemas


def test_reject_duplicate_schema():
    # Arrange: Setup database with an existing "public" schema
    existing_schema = Schema("s1", "public", "admin")
    database, _, _ = create_database({"public": existing_schema})
    new_schema = Schema("s2", "public", "admin")

    # Act & Assert: Creating a schema with duplicate name "public" should raise DuplicateSchemaError
    with pytest.raises(DuplicateSchemaError):
        database.create_schema(new_schema)


def test_get_unknown_schema():
    # Arrange: Setup database with empty schemas
    database, _, _ = create_database({})

    # Act & Assert: Getting a non-existent schema should raise UnknownSchemaError
    with pytest.raises(UnknownSchemaError):
        database.get_schema("non_existent_schema")


def test_drop_unknown_schema():
    # Arrange: Setup database with empty schemas
    database, _, _ = create_database({})

    # Act & Assert: Dropping a non-existent schema should raise UnknownSchemaError
    with pytest.raises(UnknownSchemaError):
        database.drop_schema("non_existent_schema")


def test_rename_schema_to_existing_name():
    # Arrange: Setup database with two schemas ("s1" and "s2")
    s1 = Schema("id1", "s1", "admin")
    s2 = Schema("id2", "s2", "admin")
    database, _, _ = create_database({"s1": s1, "s2": s2})

    # Act & Assert: Renaming s1 to existing name s2 should raise DuplicateSchemaError
    with pytest.raises(DuplicateSchemaError):
        database.rename_schema("s1", "s2")


def test_database_rename_updates_default_schema():
    schema = Schema("s1", "public", "admin")
    database, _, _ = create_database({"public": schema})
    database.default_schema = "public"

    database.rename_schema("public", "app")

    assert database.default_schema == "app"


def test_database_drop_default_schema_raises_value_error():
    schema = Schema("s1", "public", "admin")
    database, _, _ = create_database({"public": schema})
    database.default_schema = "public"

    with pytest.raises(ValueError, match="Cannot drop default schema"):
        database.drop_schema("public")


def test_database_open_failure_preserves_status():
    database, storage, _ = create_database()
    database.status = "closed"
    storage.load_schema_metadata.side_effect = RuntimeError("Storage error")

    with pytest.raises(RuntimeError):
        database.open()

    assert database.status == "closed"


def test_database_close_failure_preserves_status():
    database, storage, _ = create_database()
    database.status = "open"
    storage.flush_dirty_pages.side_effect = RuntimeError("Flush error")

    with pytest.raises(RuntimeError):
        database.close()

    assert database.status == "open"
