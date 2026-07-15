import codecs
from pathlib import Path
from typing import Optional

class DatabaseConfiguration:
    def __init__(self, page_size: int = 4096, encoding: str = "utf-8", max_size_mb: int = 1024, storage_location: Optional[str] = None, default_schema: str = "public"):
        self.page_size = page_size
        self.encoding = encoding
        self.max_size_mb = max_size_mb
        self.storage_location = storage_location
        self.default_schema = default_schema

class DatabaseDescriptor:
    def __init__(self, name: str, config: Optional[DatabaseConfiguration] = None):
        self.name = name
        self.config = config or DatabaseConfiguration()

class Database:
    def __init__(self, descriptor: DatabaseDescriptor):
        self.descriptor = descriptor
        self.name = descriptor.name

class DatabaseRegistry:
    def __init__(self):
        self.databases: dict[str, DatabaseDescriptor] = {}

    def register_database(self, database: DatabaseDescriptor) -> None:
        self.databases[database.name] = database

    def find_database_by_name(self, name: str) -> Optional[DatabaseDescriptor]:
        return self.databases.get(name)

    def remove_database(self, name: str) -> None:
        if name in self.databases:
            del self.databases[name]

class DatabaseManager:
    def __init__(self, registry: Optional[DatabaseRegistry] = None):
        self._registry = registry or DatabaseRegistry()
        self.databases: dict[str, Database] = {}

    def create_database(self, name: str, config: Optional[DatabaseConfiguration] = None) -> Database:
        if name in self.databases:
            raise ValueError(f"Database {name} already exists")
        cfg = config or DatabaseConfiguration()
        self._validate_database(name, cfg)
        descriptor = DatabaseDescriptor(name, cfg)
        self._registry.register_database(descriptor)
        db = Database(descriptor)
        self.databases[name] = db
        return db

    def _validate_database(self, name: str, config: DatabaseConfiguration) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Database name must be non-empty")
        if config.page_size <= 0:
            raise ValueError("Page size must be positive")
        if config.max_size_mb <= 0:
            raise ValueError("Database max size must be positive")
        try:
            codecs.lookup(config.encoding)
        except LookupError as exc:
            raise ValueError(f"Database encoding is invalid: {config.encoding}") from exc
        if config.storage_location is not None and not Path(config.storage_location).is_absolute():
            raise ValueError("Storage location must be an absolute path")
        if not isinstance(config.default_schema, str) or not config.default_schema.strip():
            raise ValueError("Default schema must be non-empty")

    def drop_database(self, name: str) -> None:
        if name in self.databases:
            self._registry.remove_database(name)
            del self.databases[name]

    def get_database(self, name: str) -> Database:
        if name not in self.databases:
            raise ValueError(f"Database {name} not found")
        return self.databases[name]

    def alter_configuration(self, name: str, config: DatabaseConfiguration) -> Database:
        self._validate_database(name, config)
        database = self.get_database(name)
        descriptor = DatabaseDescriptor(name, config)
        database.descriptor = descriptor
        self._registry.register_database(descriptor)
        return database

    def rename_database(self, name: str, new_name: str) -> Database:
        database = self.get_database(name)
        if new_name in self.databases:
            raise ValueError(f"Database {new_name} already exists")
        self._validate_database(new_name, database.descriptor.config)
        descriptor = DatabaseDescriptor(new_name, database.descriptor.config)
        self._registry.remove_database(name)
        self._registry.register_database(descriptor)
        del self.databases[name]
        database.name = new_name
        database.descriptor = descriptor
        self.databases[new_name] = database
        return database
