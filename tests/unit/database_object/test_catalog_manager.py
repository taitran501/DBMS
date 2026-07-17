from dbms.database_object.catalog_manager import CatalogManager
from unittest.mock import Mock


def test_catalog_manager_can_be_created():
    metadata_cache = object()
    catalog = CatalogManager(metadata_cache)

    assert catalog.metadata_cache is metadata_cache
    assert callable(catalog.register_object)
    assert callable(catalog.remove_object)
    assert callable(catalog.lookup_object)


def test_register_object():
    metadata_cache = Mock()
    catalog = CatalogManager(metadata_cache)
    descriptor = object()

    result = catalog.register_object("public.users", descriptor)

    assert result is True
    metadata_cache.set.assert_called_once_with("public.users", descriptor)


def test_remove_object():
    metadata_cache = Mock()
    catalog = CatalogManager(metadata_cache)

    result = catalog.remove_object("public.users")

    assert result is True
    metadata_cache.remove.assert_called_once_with("public.users")


def test_lookup_object():
    descriptor = object()
    metadata_cache = Mock()
    metadata_cache.get.return_value = descriptor
    catalog = CatalogManager(metadata_cache)

    result = catalog.lookup_object("public.users")

    assert result is descriptor
    metadata_cache.get.assert_called_once_with("public.users")
