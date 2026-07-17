from dbms.database_object.column import Column
from dbms.database_object.constraint import Constraint
from dbms.database_object.index import Index
from dbms.database_object.row import Row


class Table:
    def __init__(
        self,
        table_id: str = "",
        name: str = "",
        columns: list[Column] | None = None,
        row_count: int = 0,
        rows: dict[str, Row] | None = None,
        constraints: list[Constraint] | None = None,
        indexes: list[Index] | None = None,
    ) -> None:
        self.table_id = table_id
        self.name = name
        self.columns = [] if columns is None else columns
        self.row_count = row_count
        self.rows = {} if rows is None else rows
        self.constraints = [] if constraints is None else constraints
        self.indexes = [] if indexes is None else indexes

    def insert(self, row: Row) -> bool:
        return True

    def update(self, row_id: str, new_values: dict) -> bool:
        return True

    def delete(self, row_id: str) -> bool:
        return True

    def truncate(self) -> bool:
        return True

    def check_key_exists(self, key: object) -> bool:
        return False
