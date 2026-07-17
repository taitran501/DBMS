from dbms.database_object.partition import Partition


def test_partition_can_be_created():
    p = Partition("p1", "part_1", (1, 100))
    assert p.partition_id == "p1"
    assert p.name == "part_1"
    assert p.range == (1, 100)


def test_allocate_partition_space():
    p = Partition("p1", "part_1", (1, 100))
    assert p.allocate_space() is True


def test_release_partition_space():
    p = Partition("p1", "part_1", (1, 100))
    assert p.release_space() is True
