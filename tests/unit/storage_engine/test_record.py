from dbms.storage_engine.record import Record


def test_serialize_record():
    pass


def test_deserialize_record():
    pass


def test_record_stores_identifier_and_values():
    record = Record(1, {"name": "Ada"})

    assert record.record_id == 1
    assert record.values == {"name": "Ada"}

