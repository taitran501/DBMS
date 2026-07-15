from dataclasses import dataclass
from typing import Optional
from dbms.database_object.schema_management.schema import TableSchema
from dbms.database_object.column_management.column_manager import ColumnDescriptor
from dbms.errors import RowNotFoundError

class TableOrganization:
    HEAP = "HEAP"; INDEX_ORGANIZED = "INDEX_ORGANIZED"
class TableScope:
    PERSISTENT = "PERSISTENT"; TEMPORARY = "TEMPORARY"

@dataclass(frozen=True)
class TableDescriptor:
    name: str
    columns: tuple[ColumnDescriptor, ...]
    organization: str = TableOrganization.HEAP
    scope: str = TableScope.PERSISTENT

class Table:
    def __init__(self, name, schema, descriptor=None):
        self.name = name; self.schema = schema
        self.descriptor = descriptor or TableDescriptor(name, tuple(ColumnDescriptor(c.name, c.data_type, c.nullable, c.default_value) for c in schema.columns))
        self.rows = {}; self.next_row_id = 1

class TableManager:
    def __init__(self): self.tables = {}
    def create_table(self, schema_name, table_name, table_schema, organization=TableOrganization.HEAP, scope=TableScope.PERSISTENT):
        group = self.tables.setdefault(schema_name, {})
        if table_name in group: raise ValueError(f"Table {table_name} already exists in schema {schema_name}")
        descriptor = TableDescriptor(table_name, tuple(ColumnDescriptor(c.name, c.data_type, c.nullable, c.default_value) for c in table_schema.columns), organization, scope)
        group[table_name] = Table(table_name, table_schema, descriptor); return group[table_name]
    def drop_table(self, schema_name, table_name):
        if schema_name in self.tables: self.tables[schema_name].pop(table_name, None)
    def get_table(self, schema_name, table_name):
        try: return self.tables[schema_name][table_name]
        except KeyError as exc: raise ValueError(f"Table {table_name} not found in schema {schema_name}") from exc
    def find_table(self, table_ref):
        parts = table_ref.split(".")
        if len(parts) >= 2: return self.get_table(".".join(parts[:-1]), parts[-1])
        matches = [group[table_ref] for group in self.tables.values() if table_ref in group]
        if len(matches) != 1: raise ValueError(f"Table reference {table_ref} is missing or ambiguous")
        return matches[0]
    def insert_row(self, table, values):
        row_id = table.next_row_id; table.next_row_id += 1; table.rows[row_id] = dict(values); return row_id
    def update_row(self, table, row_id, values):
        if row_id not in table.rows: raise RowNotFoundError(str(row_id))
        previous = dict(table.rows[row_id]); table.rows[row_id] = dict(values); return previous
    def delete_row(self, table, row_id):
        if row_id not in table.rows: raise RowNotFoundError(str(row_id))
        return table.rows.pop(row_id)
    def select_rows(self, table, predicate=None):
        return tuple(dict(row, _row_id=row_id) for row_id, row in table.rows.items() if predicate is None or predicate(row))

    def rename_table(self, schema_name, table_name, new_name):
        table = self.get_table(schema_name, table_name)
        if not new_name or new_name in self.tables[schema_name]:
            raise ValueError(f"Table {new_name} already exists in schema {schema_name}")
        del self.tables[schema_name][table_name]
        table.name = new_name
        table.schema.name = new_name
        table.descriptor = TableDescriptor(new_name, table.descriptor.columns, table.descriptor.organization, table.descriptor.scope)
        self.tables[schema_name][new_name] = table
        return table

    def rename_column(self, table, column_name, new_name):
        if not new_name or new_name in table.schema.column_names():
            raise ValueError(f"Column {new_name} already exists in table {table.name}")
        column = table.schema.get_column(column_name)
        column.name = new_name
        for row in table.rows.values():
            row[new_name] = row.pop(column_name)
        columns = tuple(ColumnDescriptor(new_name if item.name == column_name else item.name, item.data_type, item.nullable, item.default_value, item.rule_set) for item in table.descriptor.columns)
        table.descriptor = TableDescriptor(table.name, columns, table.descriptor.organization, table.descriptor.scope)
        return table
