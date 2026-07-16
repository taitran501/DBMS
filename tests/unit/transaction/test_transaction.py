from dbms.transaction.transaction import Transaction
from dbms.transaction.transaction_status import TransactionStatus

def test_commit_changes():
    pass

def test_rollback_changes():
    pass

def test_create_savepoint():
    pass

def test_release_savepoint():
    pass

def test_set_isolation_level():
    pass

def test_change_state():
    pass

def test_acquire_lock():
    pass

def test_release_lock():
    pass

def test_transaction_can_be_created():
    transaction = Transaction(1, TransactionStatus.ACTIVE)
    assert transaction.transaction_id == 1
    assert transaction.status is TransactionStatus.ACTIVE
