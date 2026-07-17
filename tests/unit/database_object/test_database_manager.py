from dbms.database_object.database_manager import DatabaseManager

def test_create_database():
    pass

def test_get_database():
    pass

def test_rename_database():
    pass

def test_drop_database():
    pass

def test_reject_duplicate_database():
    pass

def test_reject_unknown_database():
    pass

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
