from dbms.database_object.index import Index


def test_index_can_be_created():
    # Arrange
    entries = {}
    index = Index("idx1", "users_age", "B-Tree", True, entries)

    # Assert
    assert index.index_id == "idx1"
    assert index.name == "users_age"
    assert index.type == "B-Tree"
    assert index.unique is True
    assert index.entries is entries
    assert callable(index.search)
    assert callable(index.insert_key)
    assert callable(index.delete_key)


def test_search():
    # Arrange
    index = Index("idx1", "users_age", "B-Tree", entries={25: ["r1"]})

    # Act
    result = index.search(25)

    # Assert
    assert result == ["r1"]


def test_insert_key():
    # Arrange
    index = Index("idx1", "users_age", "B-Tree", entries={})

    # Act
    result = index.insert_key(25, "r1")

    # Assert
    assert result is True
    assert index.entries[25] == ["r1"]


def test_delete_key():
    # Arrange
    index = Index("idx1", "users_age", "B-Tree", entries={25: ["r1"]})

    # Act
    result = index.delete_key(25, "r1")

    # Assert
    assert result is True
    assert 25 not in index.entries


def test_unique_index_rejects_a_second_row_for_the_same_key():
    # Arrange
    index = Index("idx1", "users_email", "B-Tree", unique=True)
    index.insert_key("alice@example.com", "r1")

    # Act
    result = index.insert_key("alice@example.com", "r2")

    # Assert
    assert result is False
    assert index.search("alice@example.com") == ["r1"]
