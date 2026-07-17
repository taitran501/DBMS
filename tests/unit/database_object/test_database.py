from dbms.database_object.database import Database


def create_database() -> Database:
    return Database(
        "db1",
        "test_db",
        "admin",
        "active",
        4096,
        "utf-8",
        "/data",
        "public",
        object(),
        object(),
    )


def test_database_can_be_created():
    storage = object()
    backup_service = object()
    schemas = {}
    db = Database(
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
    assert db.database_id == "db1"
    assert db.name == "test_db"
    assert db.owner == "admin"
    assert db.status == "active"
    assert db.page_size == 4096
    assert db.encoding == "utf-8"
    assert db.storage_location == "/data"
    assert db.default_schema == "public"
    assert db.storage is storage
    assert db.backup_service is backup_service
    assert db.schemas is schemas
    assert callable(db.open)
    assert callable(db.close)
    assert callable(db.backup)
    assert callable(db.restore)


def test_open():
    db = create_database()
    assert db.open() is True


def test_close():
    db = create_database()
    assert db.close() is True


def test_backup():
    db = create_database()
    assert db.backup() is True


def test_restore():
    db = create_database()
    assert db.restore() is True
