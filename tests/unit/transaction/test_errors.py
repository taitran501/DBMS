from dbms.transaction.errors import DeadlockError, LockTimeoutError


def test_deadlock_error_inherits_exception():
    assert issubclass(DeadlockError, Exception)


def test_lock_timeout_error_inherits_exception():
    assert issubclass(LockTimeoutError, Exception)
