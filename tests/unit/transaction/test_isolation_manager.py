from dbms.transaction.isolation_manager import IsolationManager

def test_read_committed():
    pass

def test_repeatable_read():
    pass

def test_serializable():
    pass

def test_snapshot_isolation():
    pass

def test_prevent_dirty_read():
    pass

def test_prevent_nonrepeatable_read():
    pass

def test_prevent_phantom_read():
    pass

def test_isolation_manager_can_be_created():
    assert isinstance(IsolationManager(), IsolationManager)
