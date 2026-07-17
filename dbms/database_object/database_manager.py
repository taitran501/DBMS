from dbms.database_object.database import Database


class DatabaseManager:
    def __init__(self) -> None:
        self.databases: dict[str, Database] = {}

    def create_database(self, name: str) -> Database | None:
        return None

    def get_database(self, name: str) -> Database | None:
        return None

    def drop_database(self, name: str) -> bool:
        return False

    def rename_database(self, old_name: str, new_name: str) -> bool:
        return False
