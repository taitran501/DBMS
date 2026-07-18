from typing import Protocol, runtime_checkable


@runtime_checkable
class LockReleaseProtocol(Protocol):
    def release_all_locks(self, transaction: object) -> bool: ...


@runtime_checkable
class TransactionStarterProtocol(Protocol):
    def begin_transaction(self, timeout: int | None = None) -> object: ...


@runtime_checkable
class RangeLockProtocol(Protocol):
    def acquire_range_lock(self, transaction: object, resource: object) -> bool: ...


@runtime_checkable
class DeadlockDetectorProtocol(Protocol):
    def detect_cycle(self, wait_graph: object) -> bool: ...


@runtime_checkable
class TransactionRecoveryLogProtocol(Protocol):
    def scan_active_records(self) -> list[object]: ...
