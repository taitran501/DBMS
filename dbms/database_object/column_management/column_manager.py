from typing import Union, Optional

class ColumnRuleSet:
    def __init__(self, is_primary_key: bool = False, is_unique: bool = False):
        self.is_primary_key = is_primary_key
        self.is_unique = is_unique

class ColumnDescriptor:
    def __init__(self, name: str, data_type: str, nullable: bool = True, default_value: Optional[str] = None, rule_set: Optional[ColumnRuleSet] = None):
        self.name = name
        self.data_type = data_type
        self.nullable = nullable
        self.default_value = default_value
        self.rule_set = rule_set or ColumnRuleSet()

class Column:
    def __init__(self, name: Union[str, ColumnDescriptor], data_type: Optional[str] = None, nullable: bool = True, default_value: Optional[str] = None):
        if isinstance(name, ColumnDescriptor):
            descriptor = name
            self.descriptor = descriptor
            self.name = descriptor.name
            self.data_type = descriptor.data_type
            self.nullable = descriptor.nullable
            self.default_value = descriptor.default_value
        else:
            self.descriptor = ColumnDescriptor(name, data_type, nullable, default_value)
            self.name = name
            self.data_type = data_type
            self.nullable = nullable
            self.default_value = default_value

class ColumnManager:
    def __init__(self):
        # table_name -> list of Column objects
        self.columns: dict[str, list[Column]] = {}

    def add_column(self, table_name: str, column: Column) -> None:
        if table_name not in self.columns:
            self.columns[table_name] = []
        if any(c.name == column.name for c in self.columns[table_name]):
            raise ValueError(f"Column {column.name} already exists in table {table_name}")
        self.columns[table_name].append(column)

    def drop_column(self, table_name: str, column_name: str) -> None:
        if table_name in self.columns:
            self.columns[table_name] = [c for c in self.columns[table_name] if c.name != column_name]

    def get_column(self, table_name: str, column_name: str) -> Column:
        if table_name in self.columns:
            for c in self.columns[table_name]:
                if c.name == column_name:
                    return c
        raise ValueError(f"Column {column_name} not found in table {table_name}")
