from dbms.durability.restore_manager import RestoreManager


def test_restore_manager_can_be_created():
    assert isinstance(RestoreManager(), RestoreManager)
