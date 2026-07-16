from dbms.transaction.deadlock_manager import DeadlockManager


def test_deadlock_manager_can_be_created():
    assert isinstance(DeadlockManager(), DeadlockManager)
