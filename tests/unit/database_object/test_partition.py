from dbms.database_object.partition import Partition


def create_partition() -> Partition:
    return Partition("p1", "part_1", (1, 100), object())


def test_partition_can_be_created():
    storage_allocator = object()
    p = Partition("p1", "part_1", (1, 100), storage_allocator)
    assert p.partition_id == "p1"
    assert p.name == "part_1"
    assert p.range == (1, 100)
    assert p.storage_allocator is storage_allocator
    assert callable(p.allocate_space)
    assert callable(p.release_space)


def test_allocate_partition_space():
    p = create_partition()
    assert p.allocate_space() is True


def test_release_partition_space():
    p = create_partition()
    assert p.release_space() is True
