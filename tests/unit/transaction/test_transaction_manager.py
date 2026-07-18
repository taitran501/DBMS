from unittest.mock import Mock

from dbms.transaction.transaction import Transaction
from dbms.transaction.transaction_manager import TransactionManager
from dbms.transaction.transaction_status import TransactionStatus


def create_manager():
    lock_manager = Mock()
    recovery_log = Mock()
    return TransactionManager(lock_manager, recovery_log), lock_manager, recovery_log


def test_transaction_manager_can_be_created():
    # Arrange
    lock_manager = Mock()
    recovery_log = Mock()

    # Act
    manager = TransactionManager(lock_manager, recovery_log)

    # Assert
    assert manager.lock_manager is lock_manager
    assert manager.recovery_log is recovery_log
    assert callable(manager.begin_transaction)
    assert callable(manager.commit)
    assert callable(manager.rollback)


def test_begin_transaction():
    # Arrange
    manager, _, _ = create_manager()

    # Act
    transaction = manager.begin_transaction()

    # Assert
    assert isinstance(transaction, Transaction)
    assert transaction.status is TransactionStatus.ACTIVE
    assert manager.active_transactions[transaction.transaction_id] is transaction


def test_commit():
    # Arrange
    manager, lock_manager, _ = create_manager()
    transaction = Transaction(1, TransactionStatus.ACTIVE)
    # Commit finalizes the transaction and frees every lock it owns.
    lock_manager.release_all_locks.return_value = True

    # Act
    result = manager.commit(transaction)

    # Assert
    assert result is True
    assert transaction.status is TransactionStatus.COMMITTED
    lock_manager.release_all_locks.assert_called_once_with(transaction)


def test_rollback():
    # Arrange
    manager, lock_manager, _ = create_manager()
    transaction = Transaction(1, TransactionStatus.ACTIVE)
    # Rollback cancels the transaction and also frees every lock it owns.
    lock_manager.release_all_locks.return_value = True

    # Act
    result = manager.rollback(transaction)

    # Assert
    assert result is True
    assert transaction.status is TransactionStatus.ROLLED_BACK
    lock_manager.release_all_locks.assert_called_once_with(transaction)


def test_rollback_to_savepoint():
    # Arrange
    manager, _, _ = create_manager()
    transaction = Mock()
    # Only work performed after this savepoint is undone.
    transaction.rollback_changes_since.return_value = True

    # Act
    result = manager.rollback_to_savepoint(transaction, "sp1")

    # Assert
    assert result is True
    transaction.rollback_changes_since.assert_called_once_with("sp1")


def test_nested_transaction():
    # Arrange
    manager, _, _ = create_manager()
    parent = Transaction(1, TransactionStatus.ACTIVE)
    # The nested transaction must retain its parent relationship.

    # Act
    nested = manager.begin_nested_transaction(parent)

    # Assert
    assert nested.parent_transaction is parent
    assert nested.status is TransactionStatus.ACTIVE


def test_distributed_transaction():
    # Arrange
    manager, _, _ = create_manager()

    # Act
    result = manager.prepare_distributed(Transaction(1, TransactionStatus.ACTIVE))

    # Assert
    assert result is True


def test_timeout():
    # Arrange
    manager, _, _ = create_manager()

    # Act
    transaction = manager.begin_transaction(timeout=2)

    # Assert
    assert transaction.timeout == 2


def test_cancel():
    # Arrange
    manager, _, _ = create_manager()
    transaction = Mock()
    manager.rollback = Mock(return_value=True)

    # Act
    result = manager.cancel(transaction)

    # Assert
    assert result is True
    manager.rollback.assert_called_once_with(transaction)


def test_retry():
    # Arrange
    manager, _, _ = create_manager()
    transaction = Mock()
    manager.rollback = Mock(return_value=True)
    manager.begin_transaction = Mock(return_value=Mock())

    # Act
    result = manager.retry(transaction)

    # Assert
    assert result is manager.begin_transaction.return_value
    manager.rollback.assert_called_once_with(transaction)
    manager.begin_transaction.assert_called_once_with()


def test_recover_transaction():
    # Arrange
    manager, _, recovery_log = create_manager()
    recovery_log.scan_active_records.return_value = [Mock()]

    # Act
    result = manager.recover_transactions()

    # Assert
    assert result is True
    recovery_log.scan_active_records.assert_called_once_with()
