from typing import List, Optional
from dbms.database_object.schema_management.schema import TableSchema
from dbms.database_object.column_management.column_manager import ColumnDescriptor

class TableOrganization:
    HEAP = "HEAP"
    INDEX_ORGANIZED = "INDEX_ORGANIZED"

class TableScope:
    PERSISTENT = "PERSISTENT"
    TEMPORARY = "TEMPORARY"

class TableDescriptor:
    def __init__(self, name: str, columns: List[ColumnDescriptor], organization: str = TableOrganization.HEAP, scope: str = TableScope.PERSISTENT):
        self.name = name
        self.columns = columns
        self.organization = organization
        self.scope = scope

class Table:
    def __init__(self, name: str, schema: TableSchema, descriptor: Optional[TableDescriptor] = None):
        self.name = name
        self.schema = schema
        self.descriptor = descriptor or TableDescriptor(
            name, 
            [ColumnDescriptor(c.name, c.data_type) for c in schema.columns]
        )

class TableManager:
    def __init__(self):
        # schema_name -> dict of tables (table_name -> Table)
        self.tables: dict[str, dict[str, Table]] = {}

    def create_table(self, schema_name: str, table_name: str, table_schema: TableSchema, organization: str = TableOrganization.HEAP, scope: str = TableScope.PERSISTENT) -> Table:
        if schema_name not in self.tables:
            self.tables[schema_name] = {}
        if table_name in self.tables[schema_name]:
            raise ValueError(f"Table {table_name} already exists in schema {schema_name}")
        
        # 1. Build TableDescriptor and ColumnDescriptors
        col_descriptors = [
            ColumnDescriptor(c.name, c.data_type) for c in table_schema.columns
        ]
        descriptor = TableDescriptor(table_name, col_descriptors, organization, scope)
        
        # 2. Create and Register Table
        table = Table(table_name, table_schema, descriptor)
        self.tables[schema_name][table_name] = table
        return table

    def drop_table(self, schema_name: str, table_name: str) -> None:
        if schema_name in self.tables and table_name in self.tables[schema_name]:
            del self.tables[schema_name][table_name]

    def get_table(self, schema_name: str, table_name: str) -> Table:
        if schema_name not in self.tables or table_name not in self.tables[schema_name]:
            raise ValueError(f"Table {table_name} not found in schema {schema_name}")
        return self.tables[schema_name][table_name]
