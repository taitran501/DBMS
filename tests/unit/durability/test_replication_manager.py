from dbms.durability.replication_manager import ReplicationManager


def test_replication_manager_can_be_created():
    assert isinstance(ReplicationManager(), ReplicationManager)
