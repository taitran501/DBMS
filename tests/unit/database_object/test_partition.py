from dbms.database_object.partition import Partition
from unittest.mock import Mock


def test_partition_can_be_created():
    storage_allocator = object()
    partition = Partition("p1", "part_1", (1, 100), storage_allocator)

    assert partition.partition_id == "p1"
    assert partition.name == "part_1"
    assert partition.range == (1, 100)
    assert partition.storage_allocator is storage_allocator
    assert callable(partition.allocate_space)
    assert callable(partition.release_space)


def test_allocate_space():
    storage_allocator = Mock()
    partition = Partition("p1", "part_1", (1, 100), storage_allocator)

    result = partition.allocate_space()

    assert result is True
    storage_allocator.allocate_space.assert_called_once_with(partition)


def test_release_space():
    storage_allocator = Mock()
    partition = Partition("p1", "part_1", (1, 100), storage_allocator)

    result = partition.release_space()

    assert result is True
    storage_allocator.release_space.assert_called_once_with(partition)
