from dbms.database_object.database import Database
from dbms.database_object.dependencies import DatabaseFactoryProtocol, DatabaseStorageProtocol


class DatabaseManager:
    def __init__(
        self,
        database_factory: DatabaseFactoryProtocol,
        storage: DatabaseStorageProtocol,
        databases: dict[str, Database],
    ) -> None:
        self.database_factory = database_factory
        self.storage = storage
        self.databases = databases

    def create_database(self, name: str) -> Database:
        return None

    def get_database(self, name: str) -> Database:
        return None

    def drop_database(self, name: str) -> bool:
        return False

    def rename_database(self, old_name: str, new_name: str) -> bool:
        return False
