from dbms.transaction.transaction_manager import TransactionManager


def test_transaction_manager_can_be_created():
    assert isinstance(TransactionManager(), TransactionManager)
