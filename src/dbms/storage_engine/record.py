import json


class Record:
    """Storage representation of one logical row."""

    def __init__(
        self,
        record_id: str | int,
        values: list | dict,
        version: str = "",
    ) -> None:
        self.record_id = record_id
        self.values = values
        self.version = version

    def serialize(self) -> bytes:
        return json.dumps(
            {
                "record_id": self.record_id,
                "values": self.values,
                "version": self.version,
            },
            separators=(",", ":"),
        ).encode("utf-8")

    @classmethod
    def deserialize(cls, payload: bytes) -> "Record":
        data = json.loads(payload.decode("utf-8"))
        return cls(data["record_id"], data["values"], data["version"])
