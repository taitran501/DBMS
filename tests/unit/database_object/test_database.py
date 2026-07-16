from dbms.database_object.database import Database


def test_database_can_be_created():
    db = Database("db1", "test_db", "admin", "active", 4096, "utf-8", "/data", "public")
    assert db.database_id == "db1"
    assert db.name == "test_db"
    assert db.owner == "admin"
    assert db.status == "active"
    assert db.page_size == 4096
    assert db.encoding == "utf-8"
    assert db.storage_location == "/data"
    assert db.default_schema == "public"


def test_open():
    db = Database("db1", "test_db", "admin", "active", 4096, "utf-8", "/data", "public")
    assert db.open() is True


def test_close():
    db = Database("db1", "test_db", "admin", "active", 4096, "utf-8", "/data", "public")
    assert db.close() is True


def test_backup():
    db = Database("db1", "test_db", "admin", "active", 4096, "utf-8", "/data", "public")
    assert db.backup() is True


def test_restore():
    db = Database("db1", "test_db", "admin", "active", 4096, "utf-8", "/data", "public")
    assert db.restore() is True
