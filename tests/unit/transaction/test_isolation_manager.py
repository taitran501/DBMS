from unittest.mock import Mock

from dbms.transaction.isolation_manager import IsolationManager


def create_manager():
    lock_manager = Mock()
    return IsolationManager(lock_manager), lock_manager


def test_isolation_manager_can_be_created():
    # Arrange
    lock_manager = Mock()

    # Act
    manager = IsolationManager(lock_manager)

    # Assert
    assert manager.lock_manager is lock_manager
    assert callable(manager.enforce_read_committed)
    assert callable(manager.enforce_repeatable_read)
    assert callable(manager.enforce_serializable)
    assert callable(manager.enforce_snapshot_isolation)


def test_read_committed():
    # Arrange
    manager, _ = create_manager()
    # A committed value is visible at this isolation level.
    row = Mock(is_committed=True, committed_value="committed")

    # Act
    result = manager.enforce_read_committed(Mock(), row)

    # Assert
    assert result == "committed"


def test_repeatable_read():
    # Arrange
    manager, _ = create_manager()
    # The transaction reads the value captured when its snapshot was created.
    transaction = Mock(snapshot={"row1": "initial"})
    row = Mock(row_id="row1")

    # Act
    result = manager.enforce_repeatable_read(transaction, row)

    # Assert
    assert result == "initial"


def test_serializable():
    # Arrange
    manager, lock_manager = create_manager()
    transaction = Mock()
    lock_manager.acquire_range_lock.return_value = True

    # Act
    result = manager.enforce_serializable(transaction, "users")

    # Assert
    assert result is True
    lock_manager.acquire_range_lock.assert_called_once_with(transaction, "users")


def test_snapshot_isolation():
    # Arrange
    manager, _ = create_manager()
    # Snapshot isolation also reads a stable, transaction-local version.
    transaction = Mock(snapshot={"row1": "snapshot"})
    row = Mock(row_id="row1")

    # Act
    result = manager.enforce_snapshot_isolation(transaction, row)

    # Assert
    assert result == "snapshot"


def test_prevent_dirty_read():
    # Arrange
    manager, _ = create_manager()
    # A row changed by an unfinished transaction is not visible.
    row = Mock(is_committed=False)

    # Act
    result = manager.read_value(Mock(), row)

    # Assert
    assert result is None


def test_prevent_nonrepeatable_read():
    # Arrange
    manager, _ = create_manager()
    # A later update must not replace the value already read by this transaction.
    transaction = Mock(initial_versions={"row1": "initial"})
    row = Mock(row_id="row1")

    # Act
    result = manager.read_value(transaction, row)

    # Assert
    assert result == "initial"


def test_prevent_phantom_read():
    # Arrange
    manager, _ = create_manager()
    # Rows inserted after the transaction snapshot are excluded from the range.
    transaction = Mock(snapshot_rows=["row1"])

    # Act
    result = manager.range_query(transaction, "users")

    # Assert
    assert result == ["row1"]
