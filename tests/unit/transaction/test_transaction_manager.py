from dbms.transaction.transaction_manager import TransactionManager
from dbms.transaction.transaction import Transaction
from dbms.transaction.transaction_status import TransactionStatus


def test_transaction_manager_returns_lifecycle_placeholders():
    manager = TransactionManager()
    transaction = Transaction(1, TransactionStatus.ACTIVE)

    assert manager.begin() is None
    assert manager.commit(transaction) is True
    assert manager.rollback(transaction) is True
