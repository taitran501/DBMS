from dbms.database_object.metadata_management.system_catalog import Catalog, MetadataManager
from dbms.database_object.database_management.database_manager import DatabaseManager
from dbms.database_object.schema_management.schema_manager import SchemaManager
from dbms.database_object.schema_management.schema import TableSchema
from dbms.database_object.table_management.table_manager import TableManager
from dbms.database_object.column_management.column_manager import ColumnManager
from dbms.database_object.data_type_management.data_type_manager import DataTypeManager
from dbms.database_object.relationship_management.relationship_manager import RelationshipManager
from dbms.database_object.index_management.index_manager import IndexManager
from dbms.database_object.view_management.view_management import ViewManager
from dbms.database_object.constraint_management.constraint_manager import ConstraintManager
from dbms.database_object.stored_procedure.stored_procedure_manager import StoredProcedureManager
from dbms.database_object.trigger_management.trigger_manager import TriggerManager
from dbms.database_object.view_management.view_management import View
from dbms.database_object.stored_procedure.stored_procedure_manager import StoredProcedure
from dbms.database_object.trigger_management.trigger_manager import Trigger

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
        self.index_manager.create_index(index_name, table_name, column_name)

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
        self.metadata_manager.register("database", name, database.descriptor)
        return database

    def provision_schema(self, database_name: str, schema_name: str, version: str = "1.0.0"):
        schema = self.schema_manager.create_schema(database_name, schema_name, version)
        self.metadata_manager.register("schema", schema_name, schema.descriptor, [f"database:{database_name}"])
        return schema

    def provision_table(self, schema_name: str, table_name: str, table_schema: TableSchema, organization="HEAP", scope="PERSISTENT"):
        for column in table_schema.columns:
            self.data_type_manager.resolve(column.data_type)
        table = self.table_manager.create_table(schema_name, table_name, table_schema, organization, scope)
        for column in table.descriptor.columns:
            from dbms.database_object.column_management.column_manager import Column
            self.column_manager.add_column(table_name, Column(column))
        self.metadata_manager.register("table", table_name, table.descriptor, [f"schema:{schema_name}"])
        self.metadata_manager.statistics_manager.update_statistics(table_name, "row_count", 0)
        return table

    def provision_view(self, schema_name: str, name: str, query: str, dependencies=None) -> View:
        view = self.view_manager.create_view(schema_name, name, query, dependencies)
        self.metadata_manager.register("view", name, view.descriptor, dependencies)
        return view

    def provision_procedure(self, schema_name: str, name: str, parameters: list[str], body: str, dependencies=None) -> StoredProcedure:
        procedure = self.stored_procedure_manager.create_procedure(schema_name, name, parameters, body)
        self.metadata_manager.register("procedure", name, procedure.descriptor, dependencies)
        return procedure

    def provision_trigger(self, table_name: str, name: str, event: str, timing: str, action: str, dependencies=None) -> Trigger:
        trigger = self.trigger_manager.create_trigger(table_name, name, event, timing, action)
        self.metadata_manager.register("trigger", name, trigger.descriptor, dependencies or [f"table:{table_name}"])
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
        row = self._normalize_row(table, values)
        self.trigger_manager.publish_table_event(table.name, "INSERT", "BEFORE", {"values": row})
        self.constraint_manager.validate_row(table.name, row, table.rows.values())
        self.relationship_manager.validate_row(table.name, row, self.table_manager)
        row_id = table.next_row_id
        self.index_manager.maintain_table_indexes(table.name, row, row_id, "INSERT")
        try:
            self.table_manager.insert_row(table, row)
            self.trigger_manager.publish_table_event(table.name, "INSERT", "AFTER", {"row_id": row_id, "values": row})
        except Exception:
            table.rows.pop(row_id, None)
            self.index_manager.maintain_table_indexes(table.name, row, row_id, "DELETE")
            raise
        self.metadata_manager.statistics_manager.update_statistics(table.name, "row_count", len(table.rows))
        self.metadata_manager.record_table_change(table.name, "INSERT")
        return row_id

    def update_row(self, table_ref: str, row_id: int, values: dict) -> dict:
        table = self.table_manager.find_table(table_ref)
        if row_id not in table.rows:
            from dbms.errors import RowNotFoundError
            raise RowNotFoundError(str(row_id))
        old = dict(table.rows[row_id]); new = dict(old); new.update(self._normalize_row(table, values, partial=True))
        self.trigger_manager.publish_table_event(table.name, "UPDATE", "BEFORE", {"row_id": row_id, "old": old, "values": new})
        others = [row for current_id, row in table.rows.items() if current_id != row_id]
        self.constraint_manager.validate_row(table.name, new, others)
        self.relationship_manager.validate_row(table.name, new, self.table_manager)
        self.index_manager.maintain_table_indexes(table.name, old, row_id, "DELETE")
        try:
            self.index_manager.maintain_table_indexes(table.name, new, row_id, "INSERT")
            table.rows[row_id] = new
            self.trigger_manager.publish_table_event(table.name, "UPDATE", "AFTER", {"row_id": row_id, "old": old, "values": new})
        except Exception:
            self.index_manager.maintain_table_indexes(table.name, new, row_id, "DELETE")
            self.index_manager.maintain_table_indexes(table.name, old, row_id, "INSERT")
            table.rows[row_id] = old
            raise
        self.metadata_manager.record_table_change(table.name, "UPDATE")
        return dict(new, _row_id=row_id)

    def delete_row(self, table_ref: str, row_id: int) -> dict:
        table = self.table_manager.find_table(table_ref)
        if row_id not in table.rows:
            from dbms.errors import RowNotFoundError
            raise RowNotFoundError(str(row_id))
        old = dict(table.rows[row_id])
        affected = []
        for relationship in self.relationship_manager.relationships.values():
            descriptor = relationship.descriptor
            if descriptor.target_table != table.name or not descriptor.target_columns:
                continue
            target_key = tuple(old.get(column) for column in descriptor.target_columns)
            child = self.table_manager.find_table(descriptor.source_table)
            matches = [(child_id, child_row) for child_id, child_row in child.rows.items() if tuple(child_row.get(column) for column in descriptor.source_columns) == target_key]
            action = relationship.policy.on_delete.upper()
            if matches and action == "NO_ACTION":
                raise ValueError(f"Relationship {relationship.name} prevents delete")
            affected.append((relationship, child, matches))
        self.trigger_manager.publish_table_event(table.name, "DELETE", "BEFORE", {"row_id": row_id, "old": old})
        self.index_manager.maintain_table_indexes(table.name, old, row_id, "DELETE")
        table.rows.pop(row_id)
        try:
            self.trigger_manager.publish_table_event(table.name, "DELETE", "AFTER", {"row_id": row_id, "old": old})
            for relationship, child, matches in affected:
                action = relationship.policy.on_delete.upper()
                for child_id, child_row in matches:
                    if action == "CASCADE":
                        self.delete_row(child.name, child_id)
                    elif action == "SET_NULL":
                        self.update_row(child.name, child_id, {column: None for column in relationship.descriptor.source_columns})
        except Exception:
            table.rows[row_id] = old
            self.index_manager.maintain_table_indexes(table.name, old, row_id, "INSERT")
            raise
        self.metadata_manager.statistics_manager.update_statistics(table.name, "row_count", len(table.rows))
        self.metadata_manager.record_table_change(table.name, "DELETE")
        return dict(old, _row_id=row_id)

    def select_rows(self, table_ref: str, predicate=None):
        return self.table_manager.select_rows(self.table_manager.find_table(table_ref), predicate)
