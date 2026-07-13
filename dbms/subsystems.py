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
            if column.data_type not in self.data_type_manager.types:
                raise ValueError(f"Data type {column.data_type} is not registered")
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
        self.trigger_manager.publish_table_event(table_name, operation, "BEFORE")
        self.constraint_manager.validate_row(table_name, values)
        self.index_manager.maintain_table_indexes(table_name, values, row_id, operation)
        matched = self.trigger_manager.publish_table_event(table_name, operation, "AFTER")
        self.metadata_manager.record_table_change(table_name, operation)
        return matched
