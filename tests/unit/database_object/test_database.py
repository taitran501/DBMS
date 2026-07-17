from dbms.database_object.database import Database
from dbms.database_object.schema import Schema
from unittest.mock import Mock


def create_database(schemas=None):
    storage = Mock()
    backup_service = Mock()
    database = Database(
        "db1", "test_db", "admin", "closed", 4096, "utf-8",
        "/data", "public", storage, backup_service, schemas,
    )
    return database, storage, backup_service


def test_database_can_be_created():
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
    database, storage, _ = create_database()
    schemas = {"public": Schema("s1", "public", "admin")}
    storage.load_schema_metadata.return_value = schemas

    result = database.open()

    assert result is True
    assert database.status == "open"
    assert database.schemas is schemas
    storage.load_schema_metadata.assert_called_once_with(database)


def test_close():
    database, storage, _ = create_database()

    result = database.close()

    assert result is True
    assert database.status == "closed"
    storage.flush_dirty_pages.assert_called_once_with(database)


def test_backup():
    database, _, backup_service = create_database()

    result = database.backup()

    assert result is True
    backup_service.create_backup.assert_called_once_with(database)


def test_restore():
    database, _, backup_service = create_database()

    result = database.restore()

    assert result is True
    backup_service.restore_backup.assert_called_once_with(database)


def test_create_schema():
    database, _, _ = create_database({})
    schema = Schema("s1", "public", "admin")

    result = database.create_schema(schema)

    assert result is True
    assert database.schemas["public"] is schema


def test_get_schema():
    schema = Schema("s1", "public", "admin")
    database, _, _ = create_database({"public": schema})

    result = database.get_schema("public")

    assert result is schema


def test_rename_schema():
    schema = Schema("s1", "public", "admin")
    database, _, _ = create_database({"public": schema})

    result = database.rename_schema("public", "application")

    assert result is True
    assert schema.name == "application"
    assert database.schemas["application"] is schema
    assert "public" not in database.schemas


def test_drop_schema():
    schema = Schema("s1", "public", "admin")
    database, _, _ = create_database({"public": schema})

    result = database.drop_schema("public")

    assert result is True
    assert "public" not in database.schemas
