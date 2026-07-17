from dbms.durability.wal_manager import WALManager


class RecoveryManager:
    def __init__(self, wal_manager: WALManager) -> None:
        self.wal_manager = wal_manager

    def recover(self) -> bool:
        return True

    def redo(self) -> bool:
        return False

    def undo(self) -> bool:
        return False
