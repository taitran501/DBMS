from dbms.transaction.transaction import Transaction
from dbms.transaction.transaction_status import TransactionStatus


def test_transaction_stores_identifier_and_status():
    transaction = Transaction(1, TransactionStatus.ACTIVE)

    assert transaction.transaction_id == 1
    assert transaction.status is TransactionStatus.ACTIVE
