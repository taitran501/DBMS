from dbms.durability.replication_manager import ReplicationManager


def test_replicate():
    pass


def test_synchronize():
    pass

def test_ship_log_record():
    pass

def test_apply_replica_log():
    pass

def test_wait_for_synchronous_replica():
    pass

def test_commit_asynchronously():
    pass

def test_detect_replica_divergence():
    pass

def test_promote_replica():
    pass

def test_reject_lagging_replica_promotion():
    pass

def test_replication_manager_can_be_created():
    assert isinstance(ReplicationManager(), ReplicationManager)
