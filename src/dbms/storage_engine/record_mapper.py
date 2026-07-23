from dbms.database_object.row import Row
from dbms.storage_engine.record import Record


class RecordMapper:
    """Maps database-object Rows to their storage Record representation."""

    def to_record(self, row: Row) -> Record:
        return Record(row.row_id, row.values, row.version)

    def to_row(self, record: Record) -> Row:
        return Row(str(record.record_id), record.values, record.version)

    def serialize(self, row: Row) -> bytes:
        return self.to_record(row).serialize()

    def deserialize(self, payload: bytes) -> Row:
        return self.to_row(Record.deserialize(payload))
