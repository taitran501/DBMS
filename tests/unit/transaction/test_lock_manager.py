import pytest
from unittest.mock import Mock

from dbms.transaction.errors import DeadlockError, LockTimeoutError
from dbms.transaction.lock_manager import LockManager


def create_manager():
    detector = Mock()
    return LockManager(detector), detector


def test_lock_manager_can_be_created():
    # Arrange / Act
    manager, detector = create_manager()

    # Assert
    assert manager.deadlock_detector is detector
    assert callable(manager.acquire_lock)
    assert callable(manager.upgrade_lock)
    assert callable(manager.downgrade_lock)
    assert callable(manager.release_lock)
    assert callable(manager.release_all_locks)


def test_acquire_lock():
    # Arrange
    manager, _ = create_manager()
    transaction = Mock()

    # Act
    result = manager.acquire_lock(transaction, "row1", "SHARED")

    # Assert
    assert result is True


def test_acquire_shared_lock():
    # Arrange
    manager, _ = create_manager()

    # Act
    result = manager.acquire_lock(Mock(), "row1", "SHARED")

    # Assert
    assert result is True


def test_acquire_exclusive_lock():
    # Arrange
    manager, _ = create_manager()

    # Act
    result = manager.acquire_lock(Mock(), "row1", "EXCLUSIVE")

    # Assert
    assert result is True


def test_upgrade_lock():
    # Arrange
    manager, _ = create_manager()
    transaction = Mock()
    # The transaction already holds a shared lock on the same row.
    manager.acquire_lock(transaction, "row1", "SHARED")

    # Act
    result = manager.upgrade_lock(transaction, "row1", "EXCLUSIVE")

    # Assert
    assert result is True


def test_downgrade_lock():
    # Arrange
    manager, _ = create_manager()
    transaction = Mock()
    # The transaction already holds an exclusive lock on the same row.
    manager.acquire_lock(transaction, "row1", "EXCLUSIVE")

    # Act
    result = manager.downgrade_lock(transaction, "row1", "SHARED")

    # Assert
    assert result is True


def test_release_lock():
    # Arrange
    manager, _ = create_manager()
    transaction = Mock()
    manager.acquire_lock(transaction, "row1", "SHARED")

    # Act
    result = manager.release_lock(transaction, "row1")

    # Assert
    assert result is True


def test_detect_deadlock():
    # Arrange
    manager, detector = create_manager()
    first_transaction = Mock(transaction_id=1)
    waiting_transaction = Mock(transaction_id=2)
    manager.acquire_lock(first_transaction, "orders:42", "EXCLUSIVE")
    detector.detect_cycle.return_value = True

    # Act / Assert
    with pytest.raises(DeadlockError):
        manager.acquire_lock(waiting_transaction, "orders:42", "EXCLUSIVE")

    detector.detect_cycle.assert_called_once()


def test_timeout_waiting():
    # Arrange
    manager, _ = create_manager()
    holder_transaction = Mock(transaction_id=1)
    waiting_transaction = Mock(transaction_id=2)
    manager.acquire_lock(holder_transaction, "orders:42", "EXCLUSIVE")

    # Act / Assert
    with pytest.raises(LockTimeoutError):
        manager.acquire_lock(waiting_transaction, "orders:42", "EXCLUSIVE", timeout=1)


def test_release_all_locks():
    # Arrange
    manager, _ = create_manager()
    transaction = Mock()
    manager.acquire_lock(transaction, "row1", "SHARED")
    manager.acquire_lock(transaction, "row2", "EXCLUSIVE")

    # Act
    result = manager.release_all_locks(transaction)

    # Assert
    assert result is True
