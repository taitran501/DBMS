from dbms.durability.recovery_manager import RecoveryManager
from dbms.durability.wal_manager import WALManager


def test_recover():
    pass


def test_redo():
    pass


def test_undo():
    pass

def test_recover_after_crash():
    pass

def test_redo_committed_transaction():
    pass

def test_undo_uncommitted_transaction():
    pass

def test_start_from_checkpoint():
    pass

def test_skip_applied_record():
    pass

def test_stop_on_corrupted_log():
    pass

def test_recover_idempotently():
    pass

def test_validate_recovered_state():
    pass

def test_recovery_manager_can_be_created():
    wal_manager = WALManager()
    manager = RecoveryManager(wal_manager)
    assert manager.wal_manager is wal_manager
