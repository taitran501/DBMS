from dbms.transaction.isolation_manager import IsolationManager


def test_isolation_manager_can_be_created():
    assert isinstance(IsolationManager(), IsolationManager)
