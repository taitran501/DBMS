from dbms.durability.log_record import LogRecord


def test_log_record_stores_change_information():
    record = LogRecord(1, "UPDATE", before_value="old", after_value="new")

    assert record.transaction_id == 1
    assert record.operation == "UPDATE"
    assert record.before_value == "old"
    assert record.after_value == "new"
