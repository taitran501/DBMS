from dbms.database_object.dependencies import DatabaseBackupProtocol, DatabaseStorageProtocol
from dbms.database_object.schema import Schema


class Database:
    def __init__(
        self,
        database_id: str,
        name: str,
        owner: str,
        status: str,
        page_size: int,
        encoding: str,
        storage_location: str,
        default_schema: str,
        storage: DatabaseStorageProtocol,
        backup_service: DatabaseBackupProtocol,
        schemas: dict[str, Schema] | None = None,
    ) -> None:
        self.database_id = database_id
        self.name = name
        self.owner = owner
        self.status = status
        self.page_size = page_size
        self.encoding = encoding
        self.storage_location = storage_location
        self.default_schema = default_schema
        self.storage = storage
        self.backup_service = backup_service
        self.schemas = {} if schemas is None else schemas

    def open(self) -> bool:
        return True

    def close(self) -> bool:
        return True

    def backup(self) -> bool:
        return True

    def restore(self) -> bool:
        return True
