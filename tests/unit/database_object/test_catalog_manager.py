from unittest.mock import Mock
import pytest

from dbms.database_object.catalog_manager import CatalogManager


def test_catalog_manager_can_be_created():
    # Arrange
    metadata_cache = object()
    catalog = CatalogManager(metadata_cache)

    # Assert
    assert catalog.metadata_cache is metadata_cache
    assert callable(catalog.register_object)
    assert callable(catalog.remove_object)
    assert callable(catalog.lookup_object)


def test_register_object():
    # Arrange
    metadata_cache = Mock()
    catalog = CatalogManager(metadata_cache)
    descriptor = object()

    # Act
    result = catalog.register_object("public.users", descriptor)

    # Assert
    assert result is True
    metadata_cache.set.assert_called_once_with("public.users", descriptor)


def test_remove_object():
    # Arrange
    metadata_cache = Mock()
    catalog = CatalogManager(metadata_cache)

    # Act
    result = catalog.remove_object("public.users")

    # Assert
    assert result is True
    metadata_cache.remove.assert_called_once_with("public.users")


def test_lookup_object():
    # Arrange
    descriptor = object()
    metadata_cache = Mock()
    metadata_cache.get.return_value = descriptor
    catalog = CatalogManager(metadata_cache)

    # Act
    result = catalog.lookup_object("public.users")

    # Assert
    assert result is descriptor
    metadata_cache.get.assert_called_once_with("public.users")


def test_lookup_unknown_object():
    # Arrange: Cache returns None for non-existent object
    metadata_cache = Mock()
    metadata_cache.get.return_value = None
    catalog = CatalogManager(metadata_cache)

    # Act & Assert: Looking up a non-existent object should raise KeyError
    with pytest.raises(KeyError):
        catalog.lookup_object("non_existent_object")


def test_remove_unknown_object():
    # Arrange: Cache raises KeyError when removing non-existent object
    metadata_cache = Mock()
    metadata_cache.remove.side_effect = KeyError("Object not found")
    catalog = CatalogManager(metadata_cache)

    # Act & Assert: Removing non-existent object should raise KeyError
    with pytest.raises(KeyError):
        catalog.remove_object("non_existent_object")


def test_register_duplicate_object():
    # Arrange: Cache raises ValueError when object name is duplicate
    metadata_cache = Mock()
    metadata_cache.set.side_effect = ValueError("Object already exists")
    catalog = CatalogManager(metadata_cache)

    # Act & Assert: Registering a duplicate object should raise ValueError
    with pytest.raises(ValueError):
        catalog.register_object("public.users", object())
