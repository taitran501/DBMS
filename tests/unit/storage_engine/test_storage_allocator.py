import pytest

from dbms.storage_engine.storage_allocator import StorageAllocator


def test_storage_allocator_can_be_created():
    # Arrange / Act
    allocator = StorageAllocator(total_space=4096)

    # Assert
    assert allocator.total_space == 4096
    assert callable(allocator.allocate_space)
    assert callable(allocator.release_space)
    assert callable(allocator.reallocate_space)
    assert callable(allocator.get_free_space)


def test_allocate_storage_space():
    # Arrange
    allocator = StorageAllocator(total_space=4096)

    # Act
    address = allocator.allocate_space(1024)

    # Assert
    assert address == 0
    assert allocator.get_free_space() == 3072


def test_release_storage_space():
    # Arrange
    allocator = StorageAllocator(total_space=4096)
    address = allocator.allocate_space(1024)

    # Act
    result = allocator.release_space(address)

    # Assert
    assert result is True
    assert allocator.get_free_space() == 4096


def test_reallocate_space():
    # Arrange
    allocator = StorageAllocator(total_space=4096)
    address = allocator.allocate_space(1024)

    # Act
    new_address = allocator.reallocate_space(address, 2048)

    # Assert
    assert new_address == 0
    assert allocator.get_free_space() == 2048


def test_track_allocator_free_space():
    # Arrange
    allocator = StorageAllocator(total_space=4096)
    allocator.allocate_space(1024)

    # Act
    result = allocator.get_free_space()

    # Assert
    assert result == 3072


def test_reject_exhausted_storage():
    # Arrange
    allocator = StorageAllocator(total_space=1024)

    # Act / Assert
    with pytest.raises(Exception, match="storage"):
        allocator.allocate_space(2048)


def test_reject_double_release():
    # Arrange
    allocator = StorageAllocator(total_space=1024)
    address = allocator.allocate_space(512)
    allocator.release_space(address)

    # Act / Assert
    with pytest.raises(Exception, match="already free"):
        allocator.release_space(address)
