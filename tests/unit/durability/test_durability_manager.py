from dbms.durability.durability_manager import DurabilityManager
from dbms.durability.recovery_manager import RecoveryManager
from dbms.durability.transaction_log_manager import TransactionLogManager


def test_durability_manager_stores_dependencies_and_returns_placeholders():
    log_manager = TransactionLogManager()
    recovery_manager = RecoveryManager(log_manager)
    manager = DurabilityManager(log_manager, recovery_manager)

    assert manager.transaction_log_manager is log_manager
    assert manager.recovery_manager is recovery_manager
    assert manager.persist(1) is True
    assert manager.recover() is True
