from dbms.transaction.dependencies import (
    DeadlockDetectorProtocol,
    LockReleaseProtocol,
    RangeLockProtocol,
    TransactionRecoveryLogProtocol,
    TransactionStarterProtocol,
)


def test_lock_release_stub_matches_protocol():
    # Arrange
    class LockReleaseStub:
        def release_all_locks(self, transaction: object) -> bool: return True

    # Assert
    assert isinstance(LockReleaseStub(), LockReleaseProtocol)


def test_transaction_starter_stub_matches_protocol():
    # Arrange
    class TransactionStarterStub:
        def begin_transaction(self, timeout: int | None = None) -> object: return object()

    # Assert
    assert isinstance(TransactionStarterStub(), TransactionStarterProtocol)


def test_range_lock_stub_matches_protocol():
    # Arrange
    class RangeLockStub:
        def acquire_range_lock(self, transaction: object, resource: object) -> bool: return True

    # Assert
    assert isinstance(RangeLockStub(), RangeLockProtocol)


def test_deadlock_detector_stub_matches_protocol():
    # Arrange
    class DeadlockDetectorStub:
        def detect_cycle(self, wait_graph: object) -> bool: return False

    # Assert
    assert isinstance(DeadlockDetectorStub(), DeadlockDetectorProtocol)


def test_transaction_recovery_log_stub_matches_protocol():
    # Arrange
    class TransactionRecoveryLogStub:
        def scan_active_records(self) -> list[object]: return []

    # Assert
    assert isinstance(TransactionRecoveryLogStub(), TransactionRecoveryLogProtocol)
