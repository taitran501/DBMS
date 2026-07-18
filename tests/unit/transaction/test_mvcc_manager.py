from dbms.transaction.mvcc_manager import MVCCManager


def test_mvcc_manager_can_be_created():
    # Arrange / Act
    manager = MVCCManager({"row1": []})

    # Assert
    assert manager.version_chain_map == {"row1": []}
    assert callable(manager.create_snapshot)
    assert callable(manager.read_visible_version)


def test_create_snapshot():
    # Arrange
    manager = MVCCManager({"row1": [(1, "Ada")]})

    # Act
    result = manager.create_snapshot(transaction_id=1)

    # Assert
    assert result == {"row1": [(1, "Ada")]}


def test_read_visible_version():
    # Arrange
    manager = MVCCManager({"row1": [(1, "old"), (2, "new")]})

    # Act
    result = manager.read_visible_version("row1", transaction_id=1)

    # Assert
    assert result == "old"
