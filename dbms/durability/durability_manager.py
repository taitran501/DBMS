from dbms.durability.recovery_manager import RecoveryManager
from dbms.durability.transaction_log_manager import TransactionLogManager


class DurabilityManager:
    def __init__(
        self,
        transaction_log_manager: TransactionLogManager,
        recovery_manager: RecoveryManager,
    ) -> None:
        self.transaction_log_manager = transaction_log_manager
        self.recovery_manager = recovery_manager

    def persist(self, transaction_id: int) -> bool:
        return True

    def recover(self) -> bool:
        return True
