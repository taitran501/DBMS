from dbms.database_object.row import Row
from dbms.storage_engine.record_mapper import RecordMapper


def test_mapper_converts_a_row_to_a_storage_record():
    row = Row("customer-1", {"name": "Ada"}, "v1")

    record = RecordMapper().to_record(row)

    assert record.record_id == "customer-1"
    assert record.values == {"name": "Ada"}
    assert record.version == "v1"


def test_mapper_serializes_and_deserializes_a_row():
    mapper = RecordMapper()
    row = Row("customer-1", {"name": "Ada"}, "v1")

    restored_row = mapper.deserialize(mapper.serialize(row))

    assert restored_row is not row
    assert restored_row.row_id == row.row_id
    assert restored_row.values == row.values
    assert restored_row.version == row.version
