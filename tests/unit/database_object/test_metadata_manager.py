from dbms.database_object.metadata_manager import MetadataManager
from dbms.database_object.system_catalog import SystemCatalog


def test_metadata_manager_stores_catalog_and_returns_placeholders():
    catalog = SystemCatalog()
    manager = MetadataManager(catalog)

    assert manager.system_catalog is catalog
    assert manager.register("users", object()) is True
    assert manager.get("users") is None
    assert manager.remove("users") is True
