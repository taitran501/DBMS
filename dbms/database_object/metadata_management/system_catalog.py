from typing import Optional
from dbms.database_object.schema_management.schema import TableSchema
from dbms.errors import DependencyExistsError, ObjectNotFoundError, TableAlreadyExistsError, TableNotFoundError

class Catalog:
    def __init__(self): self.tables: dict[str, TableSchema] = {}
    def create_table(self, schema):
        if schema.name in self.tables: raise TableAlreadyExistsError(schema.name)
        self.tables[schema.name] = schema
    def get_table(self, name):
        if name not in self.tables: raise TableNotFoundError(name)
        return self.tables[name]
    def has_table(self, name): return name in self.tables

class SystemCatalog(Catalog):
    def __init__(self):
        super().__init__(); self.objects: dict[str, object] = {}
    def add(self, key, value):
        if key in self.objects: raise ValueError(f"Metadata {key} already exists")
        self.objects[key] = value
    def update(self, key, value):
        if key not in self.objects: raise ObjectNotFoundError(key)
        self.objects[key] = value
    def get(self, key):
        if key not in self.objects: raise ObjectNotFoundError(key)
        return self.objects[key]
    def remove(self, key):
        if key not in self.objects: raise ObjectNotFoundError(key)
        return self.objects.pop(key)

class DependencyManager:
    def __init__(self): self.dependencies: dict[str, list[str]] = {}
    def register_dependency(self, source, target):
        sources = self.dependencies.setdefault(target, [])
        if source not in sources: sources.append(source)
    add_dependency = register_dependency
    def remove_source(self, source):
        for target in tuple(self.dependencies):
            self.dependencies[target] = [x for x in self.dependencies[target] if x != source]
            if not self.dependencies[target]: del self.dependencies[target]
    def dependents_of(self, target, recursive=False):
        direct = tuple(self.dependencies.get(target, ()))
        if not recursive: return direct
        found, queue = [], list(direct)
        while queue:
            current = queue.pop(0)
            if current not in found:
                found.append(current); queue.extend(self.dependencies.get(current, ()))
        return tuple(found)
    def get_dependencies(self, source):
        return tuple(target for target, sources in self.dependencies.items() if source in sources)

class StatisticsManager:
    def __init__(self): self.stats: dict[str, dict[str, int]] = {}
    def update_statistics(self, table_name, key, value): self.stats.setdefault(table_name, {})[key] = value
    def get_statistics(self, table_name, key): return self.stats.get(table_name, {}).get(key, 0)
    def increment(self, table_name, key, amount=1):
        self.update_statistics(table_name, key, self.get_statistics(table_name, key) + amount)

class MetadataManager:
    def __init__(self, catalog: Optional[Catalog] = None, dependency_manager=None, statistics_manager=None):
        self.catalog = catalog or SystemCatalog()
        self.system_catalog = self.catalog if isinstance(self.catalog, SystemCatalog) else SystemCatalog()
        self.dependency_manager = dependency_manager or DependencyManager()
        self.statistics_manager = statistics_manager or StatisticsManager()
        self.objects = self.system_catalog.objects
    def register(self, object_type, name, descriptor, dependencies=None):
        key = f"{object_type}:{name}"; self.system_catalog.add(key, descriptor)
        for dependency in dependencies or (): self.dependency_manager.register_dependency(key, dependency)
    def update(self, object_type, name, descriptor): self.system_catalog.update(f"{object_type}:{name}", descriptor)
    def remove(self, object_type, name, cascade=False):
        key = f"{object_type}:{name}"; dependents = tuple(x for x in self.dependency_manager.dependents_of(key) if x in self.objects)
        if key not in self.objects: return
        if dependents and not cascade: raise DependencyExistsError(f"{key} has dependents: {', '.join(dependents)}")
        if cascade:
            for dependent in reversed(self.dependency_manager.dependents_of(key, True)):
                if dependent in self.objects: self.system_catalog.remove(dependent)
                self.dependency_manager.remove_source(dependent)
        self.system_catalog.remove(key); self.dependency_manager.remove_source(key)
    def get(self, object_type, name):
        try: return self.system_catalog.get(f"{object_type}:{name}")
        except ObjectNotFoundError as exc: raise ValueError(f"Metadata {object_type}:{name} not found") from exc
    def record_table_change(self, table_name, operation): self.statistics_manager.increment(table_name, operation.upper())
