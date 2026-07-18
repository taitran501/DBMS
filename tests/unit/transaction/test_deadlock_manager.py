from unittest.mock import Mock

from dbms.transaction.deadlock_manager import DeadlockManager


def create_manager():
    lock_manager = Mock()
    transaction_manager = Mock()
    return DeadlockManager(lock_manager, transaction_manager), lock_manager, transaction_manager


def test_deadlock_manager_can_be_created():
    # Arrange
    lock_manager = Mock()
    transaction_manager = Mock()

    # Act
    manager = DeadlockManager(lock_manager, transaction_manager)

    # Assert
    assert manager.lock_manager is lock_manager
    assert manager.transaction_manager is transaction_manager
    assert callable(manager.build_wait_graph)
    assert callable(manager.detect_cycle)
    assert callable(manager.select_victim)


def test_build_wait_graph():
    # Arrange
    manager, _, _ = create_manager()
    holder_transaction = Mock(transaction_id=1)
    waiting_transaction = Mock(transaction_id=2)
    active_locks = {
        "orders:42": {
            "holders": [holder_transaction],
            "waiters": [waiting_transaction],
        }
    }

    # Act
    result = manager.build_wait_graph(active_locks)

    # Assert
    assert result == {waiting_transaction: {holder_transaction}}


def test_detect_cycle():
    # Arrange
    manager, _, _ = create_manager()
    first_transaction = Mock(transaction_id=1)
    second_transaction = Mock(transaction_id=2)
    wait_graph = {
        first_transaction: {second_transaction},
        second_transaction: {first_transaction},
    }

    # Act
    result = manager.detect_cycle(wait_graph)

    # Assert
    assert result is True


def test_select_victim():
    # Arrange
    manager, _, _ = create_manager()
    older_transaction = Mock(transaction_id=1)
    younger_transaction = Mock(transaction_id=2)
    cycle = [older_transaction, younger_transaction]

    # Act
    result = manager.select_victim(cycle)

    # Assert
    # The youngest transaction is the rollback victim.
    assert result is younger_transaction


def test_abort_victim():
    # Arrange
    manager, _, _ = create_manager()
    victim = Mock(transaction_id=2)
    victim.rollback.return_value = True

    # Act
    result = manager.abort_victim(victim)

    # Assert
    assert result is True
    victim.rollback.assert_called_once_with()


def test_release_victim_locks():
    # Arrange
    manager, lock_manager, _ = create_manager()
    victim = Mock()
    lock_manager.release_all_locks.return_value = True

    # Act
    result = manager.release_victim_locks(victim)

    # Assert
    assert result is True
    lock_manager.release_all_locks.assert_called_once_with(victim)


def test_retry_transaction():
    # Arrange
    manager, _, transaction_manager = create_manager()
    replacement = Mock()
    transaction_manager.begin_transaction.return_value = replacement

    # Act
    result = manager.retry_transaction(Mock(transaction_id=2))

    # Assert
    assert result is replacement
    transaction_manager.begin_transaction.assert_called_once_with()
