from dbms.transaction.lock_manager import LockManager

def test_acquire_shared_lock():
    pass

def test_acquire_exclusive_lock():
    pass

def test_upgrade_lock():
    pass

def test_downgrade_lock():
    pass

def test_release_lock():
    pass

def test_detect_deadlock():
    pass

def test_timeout_waiting():
    pass

def test_release_all_locks():
    pass

def test_lock_manager_can_be_created():
    assert isinstance(LockManager(), LockManager)
