from dbms.durability.backup_manager import BackupManager


def test_backup_manager_can_be_created():
    assert isinstance(BackupManager(), BackupManager)
