from typing import Optional

class DatabaseConfiguration:
    def __init__(self, page_size: int = 4096, encoding: str = "utf-8", max_size_mb: int = 1024):
        self.page_size = page_size
        self.encoding = encoding
        self.max_size_mb = max_size_mb

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

    def register(self, database: DatabaseDescriptor) -> None:
        self.databases[database.name] = database

    def find_by_name(self, name: str) -> Optional[DatabaseDescriptor]:
        return self.databases.get(name)

    def remove(self, name: str) -> None:
        if name in self.databases:
            del self.databases[name]

class DatabaseManager:
    def __init__(self, registry: Optional[DatabaseRegistry] = None):
        self._registry = registry or DatabaseRegistry()
        self.databases: dict[str, Database] = {}

    def create_database(self, name: str, config: Optional[DatabaseConfiguration] = None) -> Database:
        if name in self.databases:
            raise ValueError(f"Database {name} already exists")
        
        # 1. Validate DatabaseConfiguration
        cfg = config or DatabaseConfiguration()
        if cfg.page_size <= 0:
            raise ValueError("Page size must be positive")
            
        # 2. Build DatabaseDescriptor
        descriptor = DatabaseDescriptor(name, cfg)
        self._registry.register(descriptor)
        
        # 3. Create and Register database
        db = Database(descriptor)
        self.databases[name] = db
        return db

    def drop_database(self, name: str) -> None:
        if name in self.databases:
            self._registry.remove(name)
            del self.databases[name]

    def get_database(self, name: str) -> Database:
        if name not in self.databases:
            raise ValueError(f"Database {name} not found")
        return self.databases[name]

    def alter_configuration(self, name: str, config: DatabaseConfiguration) -> Database:
        if config.page_size <= 0:
            raise ValueError("Page size must be positive")
        database = self.get_database(name)
        descriptor = DatabaseDescriptor(name, config)
        database.descriptor = descriptor
        self._registry.register(descriptor)
        return database
