class WALManager:
    def __init__(self, current_lsn: int = 0) -> None:
        self.current_lsn = current_lsn

    def append(self, record: object) -> bool:
        return True

    def flush(self) -> bool:
        return True
