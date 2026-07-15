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
    def add_metadata(self, key, value):
        if key in self.objects: raise ValueError(f"Metadata {key} already exists")
        self.objects[key] = value
    def update_metadata(self, key, value):
        if key not in self.objects: raise ObjectNotFoundError(key)
        self.objects[key] = value
    def get_metadata(self, key):
        if key not in self.objects: raise ObjectNotFoundError(key)
        return self.objects[key]
    def remove_metadata(self, key):
        if key not in self.objects: raise ObjectNotFoundError(key)
        return self.objects.pop(key)

class DependencyManager:
    def __init__(self): self.dependencies: dict[str, list[str]] = {}
    def add_metadata_dependency(self, dependent, dependency):
        dependents = self.dependencies.setdefault(dependency, [])
        if dependent not in dependents: dependents.append(dependent)
    def remove_metadata_dependent(self, dependent):
        for dependency in tuple(self.dependencies):
            self.dependencies[dependency] = [x for x in self.dependencies[dependency] if x != dependent]
            if not self.dependencies[dependency]: del self.dependencies[dependency]
    def get_metadata_dependents(self, dependency, recursive=False):
        direct = tuple(self.dependencies.get(dependency, ()))
        if not recursive: return direct
        found, queue = [], list(direct)
        while queue:
            current = queue.pop(0)
            if current not in found:
                found.append(current); queue.extend(self.dependencies.get(current, ()))
        return tuple(found)
    def get_metadata_dependencies(self, dependent):
        return tuple(dep for dep, dependents in self.dependencies.items() if dependent in dependents)

    def rename_metadata_key(self, old_key, new_key):
        if old_key in self.dependencies:
            self.dependencies[new_key] = self.dependencies.pop(old_key)
        for dependency, dependents in self.dependencies.items():
            self.dependencies[dependency] = [new_key if item == old_key else item for item in dependents]

class StatisticsManager:
    def __init__(self): self.stats: dict[str, dict[str, int]] = {}
    def update_statistics(self, table_name, key, value): self.stats.setdefault(table_name, {})[key] = value
    def get_statistics(self, table_name, key): return self.stats.get(table_name, {}).get(key, 0)
    def increment_statistic(self, table_name, key, amount=1):
        self.update_statistics(table_name, key, self.get_statistics(table_name, key) + amount)

class MetadataManager:
    def __init__(self, catalog: Optional[Catalog] = None, dependency_manager=None, statistics_manager=None):
        self.catalog = catalog or SystemCatalog()
        self.system_catalog = self.catalog if isinstance(self.catalog, SystemCatalog) else SystemCatalog()
        self.dependency_manager = dependency_manager or DependencyManager()
        self.statistics_manager = statistics_manager or StatisticsManager()
        self.objects = self.system_catalog.objects
    def register_metadata(self, object_type, name, descriptor, dependencies=None):
        key = f"{object_type}:{name}"; self.system_catalog.add_metadata(key, descriptor)
        for dependency in dependencies or (): self.dependency_manager.add_metadata_dependency(key, dependency)
    def update_metadata(self, object_type, name, descriptor): self.system_catalog.update_metadata(f"{object_type}:{name}", descriptor)
    def remove_metadata(self, object_type, name, cascade=False):
        key = f"{object_type}:{name}"; dependents = tuple(x for x in self.dependency_manager.get_metadata_dependents(key) if x in self.objects)
        if key not in self.objects: return
        if dependents and not cascade: raise DependencyExistsError(f"{key} has dependents: {', '.join(dependents)}")
        if cascade:
            for dependent in reversed(self.dependency_manager.get_metadata_dependents(key, True)):
                if dependent in self.objects: self.system_catalog.remove_metadata(dependent)
                self.dependency_manager.remove_metadata_dependent(dependent)
        self.system_catalog.remove_metadata(key); self.dependency_manager.remove_metadata_dependent(key)
    def get_metadata(self, object_type, name):
        try: return self.system_catalog.get_metadata(f"{object_type}:{name}")
        except ObjectNotFoundError as exc: raise ValueError(f"Metadata {object_type}:{name} not found") from exc
    def list_metadata(self, object_type, scope=None):
        prefix = f"{object_type}:"
        if scope is not None:
            prefix = f"{prefix}{scope}."
        return tuple(sorted(key[len(f"{object_type}:"):] for key in self.objects if key.startswith(prefix)))
    def rename_metadata(self, object_type, name, new_name):
        old_key, new_key = f"{object_type}:{name}", f"{object_type}:{new_name}"
        if old_key not in self.objects:
            raise ValueError(f"Metadata {old_key} not found")
        if new_key in self.objects:
            raise ValueError(f"Metadata {new_key} already exists")
        self.objects[new_key] = self.objects.pop(old_key)
        self.dependency_manager.rename_metadata_key(old_key, new_key)
    def rename_metadata_scope(self, old_scope, new_scope):
        keys = tuple(self.objects)
        renamed = []
        for key in keys:
            object_type, name = key.split(":", 1)
            if name == old_scope or name.startswith(f"{old_scope}."):
                new_name = f"{new_scope}{name[len(old_scope):]}"
                renamed.append((object_type, name, new_name))
        for object_type, name, new_name in renamed:
            self.rename_metadata(object_type, name, new_name)
    def record_table_change(self, table_name, operation): self.statistics_manager.increment_statistic(table_name, operation.upper())
