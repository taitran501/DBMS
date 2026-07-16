from dbms.transaction.transaction_status import TransactionStatus


def test_transaction_status_defines_core_lifecycle_states():
    assert TransactionStatus.ACTIVE.name == "ACTIVE"
    assert TransactionStatus.COMMITTED.name == "COMMITTED"
    assert TransactionStatus.ROLLED_BACK.name == "ROLLED_BACK"
