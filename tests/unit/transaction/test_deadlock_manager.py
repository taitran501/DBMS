from dbms.transaction.deadlock_manager import DeadlockManager

def test_build_wait_graph():
    pass

def test_detect_cycle():
    pass

def test_select_victim():
    pass

def test_abort_victim():
    pass

def test_release_victim_locks():
    pass

def test_retry_transaction():
    pass

def test_deadlock_manager_can_be_created():
    assert isinstance(DeadlockManager(), DeadlockManager)
