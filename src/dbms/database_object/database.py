from dbms.database_object.dependencies import DatabaseBackupProtocol, DatabaseStorageProtocol
from dbms.database_object.exceptions import DuplicateSchemaError, UnknownSchemaError
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
        schemas = self.storage.load_schema_metadata(self)
        self.schemas = schemas
        self.status = "open"
        return True

    def close(self) -> bool:
        self.storage.flush_dirty_pages(self)
        self.status = "closed"
        return True

    def backup(self) -> bool:
        self.backup_service.create_backup(self)
        return True

    def restore(self) -> bool:
        self.backup_service.restore_backup(self)
        return True

    def create_schema(self, schema: Schema) -> bool:
        if schema.name in self.schemas:
            raise DuplicateSchemaError(f"Schema '{schema.name}' already exists in database '{self.name}'")
        self.schemas[schema.name] = schema
        return True

    def get_schema(self, name: str) -> Schema:
        if name not in self.schemas:
            raise UnknownSchemaError(f"Schema '{name}' not found in database '{self.name}'")
        return self.schemas[name]

    def rename_schema(self, old_name: str, new_name: str) -> bool:
        if old_name not in self.schemas:
            raise UnknownSchemaError(f"Schema '{old_name}' not found in database '{self.name}'")
        if new_name in self.schemas:
            raise DuplicateSchemaError(f"Schema '{new_name}' already exists in database '{self.name}'")
        schema = self.schemas.pop(old_name)
        schema.name = new_name
        self.schemas[new_name] = schema
        if self.default_schema == old_name:
            self.default_schema = new_name
        return True

    def drop_schema(self, name: str) -> bool:
        if name not in self.schemas:
            raise UnknownSchemaError(f"Schema '{name}' not found in database '{self.name}'")
        if name == self.default_schema:
            raise ValueError(f"Cannot drop default schema '{name}'")
        del self.schemas[name]
        return True
