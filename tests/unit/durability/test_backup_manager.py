from dbms.durability.backup_manager import BackupManager


def test_full_backup():
    pass

def test_create_full_backup():
    pass

def test_create_incremental_backup():
    pass

def test_schedule_backup():
    pass

def test_cancel_backup():
    pass

def test_verify_backup():
    pass

def test_reject_corrupted_backup():
    pass

def test_remove_incomplete_backup():
    pass

def test_backup_manager_can_be_created():
    assert isinstance(BackupManager(), BackupManager)
