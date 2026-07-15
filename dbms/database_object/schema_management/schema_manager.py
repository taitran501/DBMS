from typing import Optional

class SchemaDescriptor:
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version

class Schema:
    def __init__(self, descriptor: SchemaDescriptor):
        self.descriptor = descriptor
        self.name = descriptor.name

class SchemaCatalog:
    def __init__(self):
        self.schemas: dict[str, SchemaDescriptor] = {}

    def add_schema(self, schema: SchemaDescriptor) -> None:
        self.schemas[schema.name] = schema

    def remove_schema(self, name: str) -> None:
        if name in self.schemas:
            del self.schemas[name]

class SchemaOwnershipPolicy:
    def can_create_schema(self, actor_id: str, database_id: str) -> bool:
        return True

    def can_change_schema_owner(self, actor_id: str, schema_name: str, new_owner_id: str) -> bool:
        return True

    def can_drop_schema(self, actor_id: str, schema_name: str) -> bool:
        return True

class SchemaMigrationLedger:
    def __init__(self):
        self.history: list[str] = []

    def record_schema_migration(self, schema_name: str, op: str) -> None:
        self.history.append(f"Schema {schema_name}: {op}")

class SchemaManager:
    def __init__(self, catalog: Optional[SchemaCatalog] = None, ownership_policy: Optional[SchemaOwnershipPolicy] = None, migration_ledger: Optional[SchemaMigrationLedger] = None):
        self._catalog = catalog or SchemaCatalog()
        self._ownership_policy = ownership_policy or SchemaOwnershipPolicy()
        self._migration_ledger = migration_ledger or SchemaMigrationLedger()
        # database_name -> dict of schemas (schema_name -> Schema)
        self.schemas: dict[str, dict[str, Schema]] = {}
        self.owners: dict[tuple[str, str], str] = {}

    def create_schema(self, database_name: str, schema_name: str, version: str = "1.0.0") -> Schema:
        if database_name not in self.schemas:
            self.schemas[database_name] = {}
        if schema_name in self.schemas[database_name]:
            raise ValueError(f"Schema {schema_name} already exists in database {database_name}")
        
        # Check permissions using policy
        if not self._ownership_policy.can_create_schema("admin", database_name):
            raise PermissionError("Schema creation rejected by policy")

        # Build SchemaDescriptor
        descriptor = SchemaDescriptor(schema_name, version)
        self._catalog.add_schema(descriptor)
        self._migration_ledger.record_schema_migration(schema_name, f"Created version {version}")

        schema = Schema(descriptor)
        self.schemas[database_name][schema_name] = schema
        self.owners[(database_name, schema_name)] = "admin"
        return schema

    def drop_schema(self, database_name: str, schema_name: str) -> None:
        if database_name in self.schemas and schema_name in self.schemas[database_name]:
            if not self._ownership_policy.can_drop_schema("admin", schema_name):
                raise PermissionError("Schema deletion rejected by policy")
            self._catalog.remove_schema(schema_name)
            self._migration_ledger.record_schema_migration(schema_name, "Dropped schema")
            del self.schemas[database_name][schema_name]
            self.owners.pop((database_name, schema_name), None)

    def get_schema(self, database_name: str, schema_name: str) -> Schema:
        if database_name not in self.schemas or schema_name not in self.schemas[database_name]:
            raise ValueError(f"Schema {schema_name} not found in database {database_name}")
        return self.schemas[database_name][schema_name]

    def change_schema_owner(self, database_name: str, schema_name: str, new_owner_id: str, actor_id: str = "admin") -> None:
        self.get_schema(database_name, schema_name)
        if not self._ownership_policy.can_change_schema_owner(actor_id, schema_name, new_owner_id):
            raise PermissionError("Schema owner change rejected by policy")
        self.owners[(database_name, schema_name)] = new_owner_id
        self._migration_ledger.record_schema_migration(schema_name, f"Owner changed to {new_owner_id}")

    def rename_schema(self, database_name: str, schema_name: str, new_name: str) -> Schema:
        schema = self.get_schema(database_name, schema_name)
        if not new_name or new_name in self.schemas[database_name]:
            raise ValueError(f"Schema {new_name} already exists in database {database_name}")
        descriptor = SchemaDescriptor(new_name, schema.descriptor.version)
        self._catalog.remove_schema(schema_name)
        self._catalog.add_schema(descriptor)
        del self.schemas[database_name][schema_name]
        schema.name = new_name
        schema.descriptor = descriptor
        self.schemas[database_name][new_name] = schema
        self.owners[(database_name, new_name)] = self.owners.pop((database_name, schema_name))
        self._migration_ledger.record_schema_migration(new_name, f"Renamed from {schema_name}")
        return schema

    def get_schema_migration_history(self, schema_name: Optional[str] = None) -> tuple[str, ...]:
        history = self._migration_ledger.history
        return tuple(item for item in history if schema_name is None or item.startswith(f"Schema {schema_name}:"))

    def rename_database_scope(self, database_name: str, new_name: str) -> None:
        if new_name in self.schemas:
            raise ValueError(f"Database {new_name} already has schemas")
        self.schemas[new_name] = self.schemas.pop(database_name, {})
        self.owners = {(new_name if database == database_name else database, schema): owner for (database, schema), owner in self.owners.items()}
