from dbms.durability.transaction_log_manager import TransactionLogManager


def test_transaction_log_manager_can_be_created():
    assert isinstance(TransactionLogManager(), TransactionLogManager)
