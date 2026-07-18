from dbms.transaction.transaction import Transaction
from dbms.transaction.transaction_status import TransactionStatus


def test_transaction_can_be_created():
    # Arrange / Act
    transaction = Transaction(1, TransactionStatus.ACTIVE)

    # Assert
    assert transaction.transaction_id == 1
    assert transaction.status is TransactionStatus.ACTIVE
    assert callable(transaction.create_savepoint)
    assert callable(transaction.release_savepoint)
    assert callable(transaction.set_isolation_level)
    assert callable(transaction.change_state)


def test_create_savepoint():
    # Arrange
    transaction = Transaction(1, TransactionStatus.ACTIVE)

    # Act
    result = transaction.create_savepoint("sp1")

    # Assert
    assert result is True
    assert "sp1" in transaction.savepoints


def test_release_savepoint():
    # Arrange
    transaction = Transaction(1, TransactionStatus.ACTIVE)
    # The savepoint already exists before the release request.
    transaction.savepoints = ["sp1"]

    # Act
    result = transaction.release_savepoint("sp1")

    # Assert
    assert result is True
    assert "sp1" not in transaction.savepoints


def test_set_isolation_level():
    # Arrange
    transaction = Transaction(1, TransactionStatus.ACTIVE)

    # Act
    result = transaction.set_isolation_level("SERIALIZABLE")

    # Assert
    assert result is True
    assert transaction.isolation_level == "SERIALIZABLE"


def test_change_state():
    # Arrange
    transaction = Transaction(1, TransactionStatus.ACTIVE)

    # Act
    result = transaction.change_state(TransactionStatus.COMMITTED)

    # Assert
    assert result is True
    assert transaction.status is TransactionStatus.COMMITTED
