from dbms.database_object.metadata_management.system_catalog import Catalog, MetadataManager
from dbms.database_object.database_management.database_manager import DatabaseManager
from dbms.database_object.schema_management.schema_manager import SchemaManager
from dbms.database_object.schema_management.schema import TableSchema
from dbms.database_object.table_management.table_manager import TableManager
from dbms.database_object.column_management.column_manager import Column, ColumnManager
from dbms.database_object.data_type_management.data_type_manager import DataTypeManager
from dbms.database_object.relationship_management.relationship_manager import RelationshipManager
from dbms.database_object.index_management.index_manager import IndexManager, Index
from dbms.database_object.view_management.view_management import ViewManager
from dbms.database_object.constraint_management.constraint_manager import ConstraintManager, Constraint
from dbms.database_object.stored_procedure.stored_procedure_manager import StoredProcedureManager
from dbms.database_object.trigger_management.trigger_manager import TriggerManager
from dbms.database_object.view_management.view_management import View
from dbms.database_object.stored_procedure.stored_procedure_manager import StoredProcedure
from dbms.database_object.trigger_management.trigger_manager import Trigger
from dbms.database_object.relationship_management.relationship_manager import Relationship

class DatabaseObjectManager:
    """
    Database Object branch:
    database, schema, table, column, data type, constraint, and index management.
    """

    def __init__(
        self,
        catalog: Catalog,
        index_manager: IndexManager,
        database_manager: DatabaseManager = None,
        schema_manager: SchemaManager = None,
        table_manager: TableManager = None,
        column_manager: ColumnManager = None,
        data_type_manager: DataTypeManager = None,
        relationship_manager: RelationshipManager = None,
        constraint_manager: ConstraintManager = None,
        view_manager: ViewManager = None,
        stored_procedure_manager: StoredProcedureManager = None,
        trigger_manager: TriggerManager = None,
        metadata_manager: MetadataManager = None
    ):
        self.catalog = catalog
        self.index_manager = index_manager
        self.database_manager = database_manager if database_manager is not None else DatabaseManager()
        self.schema_manager = schema_manager if schema_manager is not None else SchemaManager()
        self.table_manager = table_manager if table_manager is not None else TableManager()
        self.column_manager = column_manager if column_manager is not None else ColumnManager()
        self.data_type_manager = data_type_manager if data_type_manager is not None else DataTypeManager()
        self.relationship_manager = relationship_manager if relationship_manager is not None else RelationshipManager()
        self.constraint_manager = constraint_manager if constraint_manager is not None else ConstraintManager()
        self.view_manager = view_manager if view_manager is not None else ViewManager()
        self.stored_procedure_manager = stored_procedure_manager if stored_procedure_manager is not None else StoredProcedureManager()
        self.trigger_manager = trigger_manager if trigger_manager is not None else TriggerManager()
        self.metadata_manager = metadata_manager if metadata_manager is not None else MetadataManager(self.catalog)

    def create_table(self, schema: TableSchema) -> None:
        self.catalog.create_table(schema)

    def get_table(self, table_name: str) -> TableSchema:
        return self.catalog.get_table(table_name)

    def has_table(self, table_name: str) -> bool:
        return self.catalog.has_table(table_name)

    def create_index(self, index_name: str, table_name: str, column_name: str) -> None:
        try:
            self.index_manager.create_index(index_name, table_name, column_name)
        except TypeError:
            self.index_manager.create_index(table_name, Index(index_name, "HASH", [column_name]))

    def maintain_index(
        self,
        index_name: str,
        key: object,
        row_id: int,
        operation: str,
    ) -> None:
        self.index_manager.maintain_index(index_name, key, row_id, operation)

    def provision_database(self, name, config=None):
        database = self.database_manager.create_database(name, config)
        self.metadata_manager.register_metadata("database", name, database.descriptor)
        return database

    @staticmethod
    def _schema_ref(database_name: str, schema_name: str) -> str:
        return f"{database_name}.{schema_name}"

    @classmethod
    def _table_ref(cls, database_name: str, schema_name: str, table_name: str) -> str:
        return f"{cls._schema_ref(database_name, schema_name)}.{table_name}"

    @staticmethod
    def _manager_table_ref(table_ref: str, table) -> str:
        """Use canonical DDL keys, while keeping the legacy short-name API intact."""
        return table_ref if table_ref.count(".") >= 2 else table.name

    @staticmethod
    def _scoped_object_name(scope: str, name: str) -> str:
        """Metadata is canonical only when the caller supplied a canonical scope."""
        return f"{scope}.{name}" if "." in scope else name

    @staticmethod
    def _split_scoped_object_name(name: str):
        return name.rsplit(".", 1) if "." in name else (None, name)

    def create_database(self, name: str, config=None):
        database = self.database_manager.create_database(name, config)
        self.metadata_manager.register_metadata("database", name, database.descriptor)
        self.create_schema(name, database.descriptor.config.default_schema)
        return database

    def create_schema(self, database_name: str, schema_name: str, version: str = "1.0.0"):
        self.database_manager.get_database(database_name)
        schema = self.schema_manager.create_schema(database_name, schema_name, version)
        self.metadata_manager.register_metadata("schema", self._schema_ref(database_name, schema_name), schema.descriptor, [f"database:{database_name}"])
        return schema

    def create_table_in_schema(self, database_name: str, schema_name: str, table_schema: TableSchema, organization="HEAP", scope="PERSISTENT"):
        self.schema_manager.get_schema(database_name, schema_name)
        for column in table_schema.columns:
            self.data_type_manager.resolve(column.data_type)
        schema_ref = self._schema_ref(database_name, schema_name)
        table = self.table_manager.create_table(schema_ref, table_schema.name, table_schema, organization, scope)
        table_ref = self._table_ref(database_name, schema_name, table_schema.name)
        for column in table.descriptor.columns:
            self.column_manager.add_column(table_ref, Column(column))
        self.metadata_manager.register_metadata("table", table_ref, table.descriptor, [f"schema:{schema_ref}"])
        self.metadata_manager.statistics_manager.update_statistics(table_ref, "row_count", 0)
        return table

    def create_index_for_table(self, database_name: str, schema_name: str, table_name: str, index: Index) -> None:
        table_ref = self._table_ref(database_name, schema_name, table_name)
        table = self.table_manager.find_table(table_ref)
        known_columns = set(table.schema.column_names())
        if not set(index.columns).issubset(known_columns):
            raise ValueError(f"Index {index.name} references an unknown column")
        self.index_manager.create_index(table_ref, index)
        self.metadata_manager.register_metadata("index", f"{table_ref}.{index.name}", index.descriptor, [f"table:{table_ref}"])

    def create_constraint_for_table(self, database_name: str, schema_name: str, table_name: str, constraint: Constraint) -> None:
        table_ref = self._table_ref(database_name, schema_name, table_name)
        table = self.table_manager.find_table(table_ref)
        if not set(constraint.columns).issubset(set(table.schema.column_names())):
            raise ValueError(f"Constraint {constraint.name} references an unknown column")
        self.constraint_manager.create_constraint(table_ref, constraint)
        self.metadata_manager.register_metadata("constraint", f"{table_ref}.{constraint.name}", constraint.descriptor, [f"table:{table_ref}"])

    def create_relationship(self, relationship: Relationship) -> None:
        descriptor = relationship.descriptor
        source = self.table_manager.find_table(descriptor.source_table)
        target = self.table_manager.find_table(descriptor.target_table)
        if not set(descriptor.source_columns).issubset(set(source.schema.column_names())) or not set(descriptor.target_columns).issubset(set(target.schema.column_names())):
            raise ValueError(f"Relationship {relationship.name} references an unknown column")
        self.relationship_manager.create_relationship(relationship)

    def drop_relationship(self, name: str) -> None:
        self.relationship_manager.drop_relationship(name)

    def drop_table_from_schema(self, database_name: str, schema_name: str, table_name: str, cascade: bool = False) -> None:
        schema_ref, table_ref = self._schema_ref(database_name, schema_name), self._table_ref(database_name, schema_name, table_name)
        self.table_manager.get_table(schema_ref, table_name)
        dependent_keys = self.metadata_manager.dependency_manager.get_metadata_dependents(f"table:{table_ref}", recursive=True) if cascade else ()
        for dependent_key in dependent_keys:
            object_type, name = dependent_key.split(":", 1)
            scope, object_name = self._split_scoped_object_name(name)
            if object_type == "view":
                if scope is not None:
                    self.view_manager.drop_view(scope, object_name)
                else:
                    for view_schema, views in tuple(self.view_manager.views.items()):
                        if object_name in views:
                            self.view_manager.drop_view(view_schema, object_name)
            if object_type == "procedure":
                if scope is not None:
                    self.stored_procedure_manager.drop_procedure(scope, object_name)
                else:
                    for procedure_schema, procedures in tuple(self.stored_procedure_manager.procedures.items()):
                        procedures.pop(object_name, None)
        self.metadata_manager.remove_metadata("table", table_ref, cascade=cascade)
        self.index_manager.indexes.pop(table_ref, None)
        self.constraint_manager.constraints.pop(table_ref, None)
        self.column_manager.columns.pop(table_ref, None)
        self.trigger_manager.triggers.pop(table_ref, None)
        self.relationship_manager.relationships = {name: relation for name, relation in self.relationship_manager.relationships.items() if table_ref not in {relation.descriptor.source_table, relation.descriptor.target_table}}
        self.metadata_manager.statistics_manager.stats.pop(table_ref, None)
        self.table_manager.drop_table(schema_ref, table_name)

    def rename_column_in_table(self, database_name: str, schema_name: str, table_name: str, column_name: str, new_name: str) -> None:
        table_ref = self._table_ref(database_name, schema_name, table_name)
        table = self.table_manager.find_table(table_ref)
        self.table_manager.rename_column(table, column_name, new_name)
        self.column_manager.rename_column(table_ref, column_name, new_name)
        self.index_manager.rename_column(table_ref, column_name, new_name)
        self.constraint_manager.rename_column(table_ref, column_name, new_name)
        self.relationship_manager.rename_column(table_ref, column_name, new_name)

    def rename_table_in_schema(self, database_name: str, schema_name: str, table_name: str, new_name: str) -> None:
        schema_ref, old_ref = self._schema_ref(database_name, schema_name), self._table_ref(database_name, schema_name, table_name)
        new_ref = self._table_ref(database_name, schema_name, new_name)
        table = self.table_manager.rename_table(schema_ref, table_name, new_name)
        self.column_manager.rename_table(old_ref, new_ref)
        self.index_manager.rename_table(old_ref, new_ref)
        self.constraint_manager.rename_table(old_ref, new_ref)
        if old_ref in self.trigger_manager.triggers:
            self.trigger_manager.triggers[new_ref] = self.trigger_manager.triggers.pop(old_ref)
        self.relationship_manager.rename_table(old_ref, new_ref)
        self.metadata_manager.update_metadata("table", old_ref, table.descriptor)
        self.metadata_manager.rename_metadata_scope(old_ref, new_ref)
        self.view_manager.rename_dependency(f"table:{old_ref}", f"table:{new_ref}")
        if old_ref in self.metadata_manager.statistics_manager.stats:
            self.metadata_manager.statistics_manager.stats[new_ref] = self.metadata_manager.statistics_manager.stats.pop(old_ref)

    def rename_database(self, database_name: str, new_name: str):
        database = self.database_manager.rename_database(database_name, new_name)
        old_prefix, new_prefix = f"{database_name}.", f"{new_name}."
        self.schema_manager.rename_database_scope(database_name, new_name)
        for old_schema_ref in tuple(self.table_manager.tables):
            if old_schema_ref.startswith(old_prefix):
                new_schema_ref = f"{new_prefix}{old_schema_ref[len(old_prefix):]}"
                self.table_manager.tables[new_schema_ref] = self.table_manager.tables.pop(old_schema_ref)
        for mapping in (self.column_manager.columns, self.index_manager.indexes, self.constraint_manager.constraints, self.trigger_manager.triggers, self.metadata_manager.statistics_manager.stats):
            for old_table_ref in tuple(mapping):
                if old_table_ref.startswith(old_prefix):
                    mapping[f"{new_prefix}{old_table_ref[len(old_prefix):]}"] = mapping.pop(old_table_ref)
        for relationship in tuple(self.relationship_manager.relationships.values()):
            self.relationship_manager.rename_table(relationship.descriptor.source_table, relationship.descriptor.source_table.replace(old_prefix, new_prefix, 1) if relationship.descriptor.source_table.startswith(old_prefix) else relationship.descriptor.source_table)
            self.relationship_manager.rename_table(relationship.descriptor.target_table, relationship.descriptor.target_table.replace(old_prefix, new_prefix, 1) if relationship.descriptor.target_table.startswith(old_prefix) else relationship.descriptor.target_table)
        self.view_manager.rename_database_scope(database_name, new_name)
        self.stored_procedure_manager.rename_database_scope(database_name, new_name)
        self.metadata_manager.rename_metadata_scope(database_name, new_name)
        return database

    def drop_database(self, database_name: str, cascade: bool = False) -> None:
        database_key = f"database:{database_name}"
        if not cascade:
            self.metadata_manager.remove_metadata("database", database_name)
        for schema_name, tables in tuple(self.table_manager.tables.items()):
            if schema_name.startswith(f"{database_name}."):
                for table_name in tuple(tables):
                    self.drop_table_from_schema(database_name, schema_name.split(".", 1)[1], table_name, cascade=True)
        for schema_name in tuple(self.schema_manager.schemas.get(database_name, {})):
            schema_ref = self._schema_ref(database_name, schema_name)
            if f"schema:{schema_ref}" in self.metadata_manager.objects:
                self.metadata_manager.remove_metadata("schema", schema_ref, cascade=True)
            self.schema_manager.drop_schema(database_name, schema_name)
        self.schema_manager.schemas.pop(database_name, None)
        if database_key in self.metadata_manager.objects:
            self.metadata_manager.remove_metadata("database", database_name, cascade=True)
        self.database_manager.drop_database(database_name)

    def provision_schema(self, database_name: str, schema_name: str, version: str = "1.0.0"):
        schema = self.schema_manager.create_schema(database_name, schema_name, version)
        self.metadata_manager.register_metadata("schema", schema_name, schema.descriptor, [f"database:{database_name}"])
        return schema

    def provision_table(self, schema_name: str, table_name: str, table_schema: TableSchema, organization="HEAP", scope="PERSISTENT"):
        for column in table_schema.columns:
            self.data_type_manager.resolve(column.data_type)
        table = self.table_manager.create_table(schema_name, table_name, table_schema, organization, scope)
        for column in table.descriptor.columns:
            from dbms.database_object.column_management.column_manager import Column
            self.column_manager.add_column(table_name, Column(column))
        self.metadata_manager.register_metadata("table", table_name, table.descriptor, [f"schema:{schema_name}"])
        self.metadata_manager.statistics_manager.update_statistics(table_name, "row_count", 0)
        return table

    def provision_view(self, schema_name: str, name: str, query: str, dependencies=None) -> View:
        view = self.view_manager.create_view(schema_name, name, query, dependencies)
        self.metadata_manager.register_metadata("view", self._scoped_object_name(schema_name, name), view.descriptor, dependencies)
        return view

    def provision_procedure(self, schema_name: str, name: str, parameters: list[str], body: str, dependencies=None) -> StoredProcedure:
        procedure = self.stored_procedure_manager.create_procedure(schema_name, name, parameters, body)
        self.metadata_manager.register_metadata("procedure", self._scoped_object_name(schema_name, name), procedure.descriptor, dependencies)
        return procedure

    def provision_trigger(self, table_name: str, name: str, event: str, timing: str, action: str, dependencies=None) -> Trigger:
        trigger = self.trigger_manager.create_trigger(table_name, name, event, timing, action)
        self.metadata_manager.register_metadata("trigger", self._scoped_object_name(table_name, name), trigger.descriptor, dependencies or [f"table:{table_name}"])
        return trigger

    def apply_table_event(self, table_name: str, operation: str, values: dict, row_id: int) -> list[Trigger]:
        context = {"table": table_name, "operation": operation.upper(), "row_id": row_id, "values": values}
        self.trigger_manager.publish_table_event(table_name, operation, "BEFORE", context)
        self.constraint_manager.validate_row(table_name, values)
        self.index_manager.maintain_table_indexes(table_name, values, row_id, operation)
        matched = self.trigger_manager.publish_table_event(table_name, operation, "AFTER", context)
        self.metadata_manager.record_table_change(table_name, operation)
        return matched

    def _normalize_row(self, table, values, partial=False):
        result = dict(values)
        known = {column.name for column in table.descriptor.columns}
        unknown = set(result) - known
        if unknown:
            raise ValueError(f"Unknown columns: {', '.join(sorted(unknown))}")
        for column in table.descriptor.columns:
            if partial and column.name not in result:
                continue
            value = result.get(column.name, column.default_value)
            data_type = self.data_type_manager.resolve(column.data_type)
            value = self.data_type_manager.convert_value(data_type, value)
            if value is None and not column.nullable:
                raise ValueError(f"Column {column.name} cannot be null")
            if value is not None and not self.data_type_manager.validate_value(data_type, value):
                raise ValueError(f"Invalid value for {column.name}: expected {column.data_type}")
            result[column.name] = value
        return result

    def insert_row(self, table_ref: str, values: dict) -> int:
        table = self.table_manager.find_table(table_ref)
        manager_ref = self._manager_table_ref(table_ref, table)
        row = self._normalize_row(table, values)
        self.trigger_manager.publish_table_event(manager_ref, "INSERT", "BEFORE", {"values": row})
        self.constraint_manager.validate_row(manager_ref, row, table.rows.values())
        self.relationship_manager.validate_row(manager_ref, row, self.table_manager)
        row_id = table.next_row_id
        self.index_manager.maintain_table_indexes(manager_ref, row, row_id, "INSERT")
        try:
            self.table_manager.insert_row(table, row)
            self.trigger_manager.publish_table_event(manager_ref, "INSERT", "AFTER", {"row_id": row_id, "values": row})
        except Exception:
            table.rows.pop(row_id, None)
            self.index_manager.maintain_table_indexes(manager_ref, row, row_id, "DELETE")
            raise
        self.metadata_manager.statistics_manager.update_statistics(manager_ref, "row_count", len(table.rows))
        self.metadata_manager.record_table_change(manager_ref, "INSERT")
        return row_id

    def update_row(self, table_ref: str, row_id: int, values: dict) -> dict:
        table = self.table_manager.find_table(table_ref)
        manager_ref = self._manager_table_ref(table_ref, table)
        if row_id not in table.rows:
            from dbms.errors import RowNotFoundError
            raise RowNotFoundError(str(row_id))
        old = dict(table.rows[row_id]); new = dict(old); new.update(self._normalize_row(table, values, partial=True))
        self.trigger_manager.publish_table_event(manager_ref, "UPDATE", "BEFORE", {"row_id": row_id, "old": old, "values": new})
        others = [row for current_id, row in table.rows.items() if current_id != row_id]
        self.constraint_manager.validate_row(manager_ref, new, others)
        self.relationship_manager.validate_row(manager_ref, new, self.table_manager)
        dependent_updates = []
        for relationship in self.relationship_manager.relationships.values():
            descriptor = relationship.descriptor
            if descriptor.target_table not in {table.name, table_ref, manager_ref} or not descriptor.target_columns:
                continue
            old_key = tuple(old.get(column) for column in descriptor.target_columns)
            new_key = tuple(new.get(column) for column in descriptor.target_columns)
            if old_key == new_key:
                continue
            child = self.table_manager.find_table(descriptor.source_table)
            matches = [(child_id, child_row) for child_id, child_row in child.rows.items() if tuple(child_row.get(column) for column in descriptor.source_columns) == old_key]
            action = relationship.policy.on_update.upper()
            if matches and action == "NO_ACTION":
                raise ValueError(f"Relationship {relationship.name} prevents update")
            if action not in {"NO_ACTION", "CASCADE", "SET_NULL"}:
                raise ValueError(f"Relationship {relationship.name} has unsupported on_update action")
            dependent_updates.append((relationship, child, matches, new_key))
        self.index_manager.maintain_table_indexes(manager_ref, old, row_id, "DELETE")
        try:
            self.index_manager.maintain_table_indexes(manager_ref, new, row_id, "INSERT")
            table.rows[row_id] = new
            for relationship, child, matches, new_key in dependent_updates:
                action = relationship.policy.on_update.upper()
                for child_id, _ in matches:
                    replacement = {column: (None if action == "SET_NULL" else new_key[position]) for position, column in enumerate(relationship.descriptor.source_columns)}
                    child_ref = self._manager_table_ref(descriptor.source_table, child)
                    self.update_row(child_ref, child_id, replacement)
            self.trigger_manager.publish_table_event(manager_ref, "UPDATE", "AFTER", {"row_id": row_id, "old": old, "values": new})
        except Exception:
            self.index_manager.maintain_table_indexes(manager_ref, new, row_id, "DELETE")
            self.index_manager.maintain_table_indexes(manager_ref, old, row_id, "INSERT")
            table.rows[row_id] = old
            raise
        self.metadata_manager.record_table_change(manager_ref, "UPDATE")
        return dict(new, _row_id=row_id)

    def delete_row(self, table_ref: str, row_id: int) -> dict:
        table = self.table_manager.find_table(table_ref)
        manager_ref = self._manager_table_ref(table_ref, table)
        if row_id not in table.rows:
            from dbms.errors import RowNotFoundError
            raise RowNotFoundError(str(row_id))
        old = dict(table.rows[row_id])
        affected = []
        for relationship in self.relationship_manager.relationships.values():
            descriptor = relationship.descriptor
            if descriptor.target_table not in {table.name, table_ref, manager_ref} or not descriptor.target_columns:
                continue
            target_key = tuple(old.get(column) for column in descriptor.target_columns)
            child = self.table_manager.find_table(descriptor.source_table)
            matches = [(child_id, child_row) for child_id, child_row in child.rows.items() if tuple(child_row.get(column) for column in descriptor.source_columns) == target_key]
            action = relationship.policy.on_delete.upper()
            if matches and action == "NO_ACTION":
                raise ValueError(f"Relationship {relationship.name} prevents delete")
            affected.append((relationship, child, matches))
        self.trigger_manager.publish_table_event(manager_ref, "DELETE", "BEFORE", {"row_id": row_id, "old": old})
        self.index_manager.maintain_table_indexes(manager_ref, old, row_id, "DELETE")
        table.rows.pop(row_id)
        try:
            self.trigger_manager.publish_table_event(manager_ref, "DELETE", "AFTER", {"row_id": row_id, "old": old})
            for relationship, child, matches in affected:
                action = relationship.policy.on_delete.upper()
                for child_id, child_row in matches:
                    if action == "CASCADE":
                        self.delete_row(self._manager_table_ref(relationship.descriptor.source_table, child), child_id)
                    elif action == "SET_NULL":
                        self.update_row(self._manager_table_ref(relationship.descriptor.source_table, child), child_id, {column: None for column in relationship.descriptor.source_columns})
        except Exception:
            table.rows[row_id] = old
            self.index_manager.maintain_table_indexes(manager_ref, old, row_id, "INSERT")
            raise
        self.metadata_manager.statistics_manager.update_statistics(manager_ref, "row_count", len(table.rows))
        self.metadata_manager.record_table_change(manager_ref, "DELETE")
        return dict(old, _row_id=row_id)

    def select_rows(self, table_ref: str, predicate=None):
        return self.table_manager.select_rows(self.table_manager.find_table(table_ref), predicate)
