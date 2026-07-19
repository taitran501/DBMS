from dbms.durability.wal_manager import WALManager


def test_wal_manager_can_be_created():
    # Arrange / Act
    manager = WALManager(current_lsn=7)

    # Assert: a restored WAL continues from its persisted log sequence number.
    assert manager.current_lsn == 7
    assert callable(manager.append)
    assert callable(manager.flush)


def test_append():
    # Arrange
    manager = WALManager(current_lsn=0)
    record = object()

    # Act
    result = manager.append(record)

    # Assert: each appended record advances the ordering sequence exactly once.
    assert result is True
    assert manager.current_lsn == 1


def test_flush():
    # Arrange
    manager = WALManager()

    # Act / Assert: flush reports whether pending WAL data reached durable storage.
    assert manager.flush() is True
