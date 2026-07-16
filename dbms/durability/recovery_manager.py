from dbms.durability.transaction_log_manager import TransactionLogManager


class RecoveryManager:
    def __init__(self, transaction_log_manager: TransactionLogManager) -> None:
        self.transaction_log_manager = transaction_log_manager

    def recover(self) -> bool:
        return True

    def rollback(self, transaction_id: int) -> bool:
        return True
