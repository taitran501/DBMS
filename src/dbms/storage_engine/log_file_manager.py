import hashlib


class LogFileManager:
    """Manages WAL (Write-Ahead Logging) log sequence entries, checksum validation, and truncation."""

    def __init__(self) -> None:
        self.current_lsn: int = 0
        self.entries: dict[int, tuple[bytes, str]] = {}

    def _compute_checksum(self, data: bytes) -> str:
        return hashlib.md5(data).hexdigest()

    def append_log_entry(self, data: bytes) -> int:
        self.current_lsn += 1
        checksum = self._compute_checksum(data)
        self.entries[self.current_lsn] = (data, checksum)
        return self.current_lsn

    def read_log_entry(self, lsn: int) -> bytes | None:
        if lsn not in self.entries:
            return None
        data, checksum = self.entries[lsn]
        if checksum != self._compute_checksum(data):
            raise Exception("Invalid checksum for log entry")
        return data

    def read_log_range(self, start_lsn: int, end_lsn: int) -> list[bytes]:
        result = []
        for lsn in range(start_lsn, end_lsn + 1):
            entry = self.read_log_entry(lsn)
            if entry is not None:
                result.append(entry)
        return result

    def flush_log(self) -> bool:
        return True

    def truncate_log(self, up_to_lsn: int) -> bool:
        keys_to_delete = [lsn for lsn in self.entries.keys() if lsn < up_to_lsn]
        for key in keys_to_delete:
            del self.entries[key]
        return True
