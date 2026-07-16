from dbms.transaction.lock_manager import LockManager


def test_lock_manager_can_be_created():
    assert isinstance(LockManager(), LockManager)
