from dbms.durability.recovery_manager import RecoveryManager
from dbms.durability.transaction_log_manager import TransactionLogManager


def test_recovery_manager_stores_log_manager_and_returns_placeholders():
    log_manager = TransactionLogManager()
    manager = RecoveryManager(log_manager)

    assert manager.transaction_log_manager is log_manager
    assert manager.recover() is True
    assert manager.rollback(1) is True
