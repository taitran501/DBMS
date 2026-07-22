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
        if row.row_id in self.rows:
            raise ValueError(f"Row '{row.row_id}' already exists")
        self._validate_constraints(row)
        self.rows[row.row_id] = row
        self.row_count += 1
        return True

    def update(self, row_id: str, new_values: dict) -> bool:
        if row_id not in self.rows:
            raise KeyError(f"Row '{row_id}' does not exist")

        row = self.rows[row_id]
        if self.constraints:
            candidate = Row(row_id, dict(new_values), row.version)
            self._validate_constraints(candidate)
        return bool(row.update(new_values))

    def delete(self, row_id: str) -> bool:
        return True

    def truncate(self) -> bool:
        return True

    def check_key_exists(self, key: object) -> bool:
        return False

    def _validate_constraints(self, row: Row) -> None:
        existing_rows = tuple(self.rows.values())
        for constraint in self.constraints:
            if not constraint.validate_row(row, existing_rows=existing_rows):
                raise ValueError(
                    f"Constraint '{constraint.name}' rejected row '{row.row_id}'"
                )
