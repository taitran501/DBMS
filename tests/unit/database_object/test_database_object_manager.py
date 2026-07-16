from dbms.database_object.database_object_manager import DatabaseObjectManager
from dbms.database_object.metadata_manager import MetadataManager
from dbms.database_object.system_catalog import SystemCatalog


def test_database_object_manager_stores_metadata_manager_and_returns_placeholders():
    metadata_manager = MetadataManager(SystemCatalog())
    manager = DatabaseObjectManager(metadata_manager)

    assert manager.metadata_manager is metadata_manager
    assert manager.get_object("users") is None
    assert manager.object_exists("users") is True
