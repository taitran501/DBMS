class Record:
    def __init__(self, record_id: int, values: dict[str, object]) -> None:
        self.record_id = record_id
        self.values = values
