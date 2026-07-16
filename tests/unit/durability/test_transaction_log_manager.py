from dbms.durability.log_record import LogRecord
from dbms.durability.transaction_log_manager import TransactionLogManager


def test_transaction_log_manager_returns_placeholder_results():
    manager = TransactionLogManager()
    record = LogRecord(1, "INSERT")

    assert manager.append(record) is True
    assert manager.read_entries(1) == []
