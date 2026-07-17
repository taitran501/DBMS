from dbms.database_object.catalog_manager import CatalogManager


def test_catalog_manager_can_be_created():
    metadata_cache = object()
    catalog = CatalogManager(metadata_cache)

    assert catalog.metadata_cache is metadata_cache
    assert callable(catalog.register_object)
    assert callable(catalog.remove_object)
    assert callable(catalog.lookup_object)


def test_register_object():
    pass


def test_remove_object():
    pass


def test_lookup_object():
    pass
