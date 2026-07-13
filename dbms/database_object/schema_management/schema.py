class ColumnSchema:
    def __init__(self, name: str, data_type: str, nullable: bool = True, default_value=None):
        self.name = name
        self.data_type = data_type
        self.nullable = nullable
        self.default_value = default_value


class TableSchema:
    def __init__(self, name: str, columns: list[ColumnSchema]):
        self.name = name
        self.columns = columns

    def column_names(self) -> list[str]:
        return [column.name for column in self.columns]

    def get_column(self, name: str) -> ColumnSchema:
        for column in self.columns:
            if column.name == name:
                return column
        from dbms.errors import ColumnNotFoundError
        raise ColumnNotFoundError(name)
