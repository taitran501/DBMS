from typing import Optional
from dbms.database_object.schema_management.schema import TableSchema
from dbms.errors import TableAlreadyExistsError, TableNotFoundError

class Catalog:
    def __init__(self):
        self.tables: dict[str, TableSchema] = {}

    def create_table(self, schema: TableSchema) -> None:
        if schema.name in self.tables:
            raise TableAlreadyExistsError(schema.name)

        self.tables[schema.name] = schema

    def get_table(self, table_name: str) -> TableSchema:
        if table_name not in self.tables:
            raise TableNotFoundError(table_name)

        return self.tables[table_name]

    def has_table(self, table_name: str) -> bool:
        return table_name in self.tables

class SystemCatalog(Catalog):
    pass

class DependencyManager:
    def __init__(self):
        self.dependencies: dict[str, list[str]] = {}

    def register_dependency(self, source: str, target: str) -> None:
        if target not in self.dependencies:
            self.dependencies[target] = []
        if source not in self.dependencies[target]:
            self.dependencies[target].append(source)

class StatisticsManager:
    def __init__(self):
        self.stats: dict[str, dict[str, int]] = {}

    def update_statistics(self, table_name: str, key: str, value: int) -> None:
        if table_name not in self.stats:
            self.stats[table_name] = {}
        self.stats[table_name][key] = value

    def get_statistics(self, table_name: str, key: str) -> int:
        return self.stats.get(table_name, {}).get(key, 0)

class MetadataManager:
    def __init__(self, catalog: Optional[Catalog] = None, dependency_manager: Optional[DependencyManager] = None, statistics_manager: Optional[StatisticsManager] = None):
        self.catalog = catalog or SystemCatalog()
        self.dependency_manager = dependency_manager or DependencyManager()
        self.statistics_manager = statistics_manager or StatisticsManager()
        self.objects: dict[str, object] = {}

    def register(self, object_type: str, name: str, descriptor: object, dependencies: Optional[list[str]] = None) -> None:
        object_id = f"{object_type}:{name}"
        if object_id in self.objects:
            raise ValueError(f"Metadata {object_id} already exists")
        self.objects[object_id] = descriptor
        for dependency in dependencies or []:
            self.dependency_manager.register_dependency(object_id, dependency)

    def remove(self, object_type: str, name: str) -> None:
        self.objects.pop(f"{object_type}:{name}", None)

    def get(self, object_type: str, name: str) -> object:
        object_id = f"{object_type}:{name}"
        if object_id not in self.objects:
            raise ValueError(f"Metadata {object_id} not found")
        return self.objects[object_id]

    def record_table_change(self, table_name: str, operation: str) -> None:
        key = operation.upper()
        current = self.statistics_manager.get_statistics(table_name, key)
        self.statistics_manager.update_statistics(table_name, key, current + 1)
