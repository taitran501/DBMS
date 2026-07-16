from dbms.durability.log_record import LogRecord


class TransactionLogManager:
    def append(self, record: LogRecord) -> bool:
        return True

    def read_entries(self, transaction_id: int) -> list[LogRecord]:
        return []
