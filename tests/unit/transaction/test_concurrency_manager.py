from dbms.transaction.concurrency_manager import ConcurrencyManager


def test_concurrency_manager_can_be_created():
    assert isinstance(ConcurrencyManager(), ConcurrencyManager)
