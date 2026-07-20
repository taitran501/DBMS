import pytest

from dbms.storage_engine.exceptions import StorageExhaustedError
from dbms.storage_engine.storage_allocator import StorageAllocator


def test_storage_allocator_can_be_created():
    """Ensure StorageAllocator initializes with correct total capacity and methods."""
    # Arrange / Act
    allocator = StorageAllocator(total_space=4096)

    # Assert
    assert allocator.total_space == 4096
    assert callable(allocator.allocate_space)
    assert callable(allocator.release_space)
    assert callable(allocator.reallocate_space)
    assert callable(allocator.get_free_space)


def test_allocate_storage_space():
    """Ensure allocating space returns offset address and reduces available free space."""
    # Arrange
    allocator = StorageAllocator(total_space=4096)

    # Act
    address = allocator.allocate_space(1024)

    # Assert
    assert address == 0
    assert allocator.get_free_space() == 3072


def test_release_storage_space():
    """Ensure releasing allocated space frees up memory back to allocator capacity."""
    # Arrange
    allocator = StorageAllocator(total_space=4096)
    address = allocator.allocate_space(1024)

    # Act
    result = allocator.release_space(address)

    # Assert
    assert result is True
    assert allocator.get_free_space() == 4096


def test_reallocate_space():
    """Ensure reallocating space expands existing allocation offset correctly."""
    # Arrange
    allocator = StorageAllocator(total_space=4096)
    address = allocator.allocate_space(1024)

    # Act
    new_address = allocator.reallocate_space(address, 2048)

    # Assert
    assert new_address == 0
    assert allocator.get_free_space() == 2048


def test_track_allocator_free_space():
    """Ensure get_free_space correctly tracks available unallocated storage bytes."""
    # Arrange
    allocator = StorageAllocator(total_space=4096)
    allocator.allocate_space(1024)

    # Act
    result = allocator.get_free_space()

    # Assert
    assert result == 3072


def test_reject_exhausted_storage():
    """Ensure requesting more storage than total available capacity raises an Exception."""
    # Arrange
    allocator = StorageAllocator(total_space=1024)

    # Act & Assert: Allocating 2048 bytes from 1024 total capacity fails
    with pytest.raises(Exception, match="storage"):
        allocator.allocate_space(2048)


def test_reject_double_release():
    """Ensure releasing an already freed storage address raises an Exception to prevent corruption."""
    # Arrange
    allocator = StorageAllocator(total_space=1024)
    address = allocator.allocate_space(512)
    allocator.release_space(address)

    # Act & Assert: Re-releasing the same address fails
    with pytest.raises(Exception, match="already free"):
        allocator.release_space(address)


def test_failed_reallocation_preserves_original_allocation():
    """Ensure that if reallocating to a larger size fails due to storage exhaustion,
    the original space allocation remains intact and unchanged.
    """
    # Arrange: Setup allocator with 1024 total bytes and allocate 512 bytes
    allocator = StorageAllocator(total_space=1024)
    address = allocator.allocate_space(512)

    # Act & Assert: Attempting to grow allocation to 2048 bytes fails with StorageExhaustedError
    with pytest.raises(StorageExhaustedError):
        allocator.reallocate_space(address, 2048)

    # Verify original 512 bytes stay allocated and can still be freed
    assert allocator.get_free_space() == 512
    assert allocator.release_space(address) is True
