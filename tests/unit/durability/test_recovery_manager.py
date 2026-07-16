from dbms.durability.recovery_manager import RecoveryManager


def test_recovery_manager_can_be_created():
    assert isinstance(RecoveryManager(), RecoveryManager)
