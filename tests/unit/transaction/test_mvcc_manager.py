from dbms.transaction.mvcc_manager import MVCCManager


def test_mvcc_manager_can_be_created():
    mvcc = MVCCManager({"row1": []})
    assert mvcc.version_chain_map == {"row1": []}


def test_create_snapshot():
    mvcc = MVCCManager({"row1": []})
    assert mvcc.create_snapshot() is None


def test_read_visible_version():
    mvcc = MVCCManager({"row1": []})
    row = object()
    tx = object()
    assert mvcc.read_visible_version(row, tx) is row
