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
    pass


def test_insert_key():
    pass


def test_delete_key():
    pass
