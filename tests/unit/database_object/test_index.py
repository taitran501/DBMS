from dbms.database_object.index import Index


def test_index_can_be_created():
    entries = {}
    index = Index("idx1", "users_age", "B-Tree", True, entries)

    assert index.index_id == "idx1"
    assert index.name == "users_age"
    assert index.type == "B-Tree"
    assert index.unique is True
    assert index.entries is entries
    assert callable(index.search)
    assert callable(index.insert_key)
    assert callable(index.delete_key)


def test_search():
    index = Index("idx1", "users_age", "B-Tree", entries={25: ["r1"]})

    result = index.search(25)

    assert result == ["r1"]


def test_insert_key():
    index = Index("idx1", "users_age", "B-Tree", entries={})

    result = index.insert_key(25, "r1")

    assert result is True
    assert index.entries[25] == ["r1"]


def test_delete_key():
    index = Index("idx1", "users_age", "B-Tree", entries={25: ["r1"]})

    result = index.delete_key(25, "r1")

    assert result is True
    assert 25 not in index.entries
