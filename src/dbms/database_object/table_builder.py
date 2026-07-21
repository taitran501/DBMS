from __future__ import annotations

from dbms.database_object.column import Column
from dbms.database_object.constraint import Constraint
from dbms.database_object.data_type import DataType
from dbms.database_object.index import Index
from dbms.database_object.table import Table


class TableBuilder:
    """Builder pattern implementation for constructing Table objects step-by-step."""

    def __init__(self, name: str, table_id: str = "") -> None:
        if not name:
            raise ValueError("Table name cannot be empty")
        self.name = name
        self.table_id = table_id
        self._columns: list[Column] = []
        self._constraints: list[Constraint] = []
        self._indexes: list[Index] = []

    def set_table_id(self, table_id: str) -> TableBuilder:
        self.table_id = table_id
        return self

    def add_column(
        self,
        name: str,
        data_type: DataType | str,
        column_id: str = "",
        nullable: bool = True,
    ) -> TableBuilder:
        if any(col.name == name for col in self._columns):
            raise ValueError(f"Column '{name}' already exists in builder")

        if isinstance(data_type, str):
            dt = DataType(data_type, lambda v: True, str)
        else:
            dt = data_type

        col_id = column_id or f"col_{len(self._columns) + 1}"
        col = Column(col_id, name, dt, nullable=nullable)
        self._columns.append(col)
        return self

    def add_column_object(self, column: Column) -> TableBuilder:
        if any(col.name == column.name for col in self._columns):
            raise ValueError(f"Column '{column.name}' already exists in builder")
        self._columns.append(column)
        return self

    def add_constraint(self, constraint: Constraint) -> TableBuilder:
        self._constraints.append(constraint)
        return self

    def add_index(self, index: Index) -> TableBuilder:
        self._indexes.append(index)
        return self

    def build(self) -> Table:
        return Table(
            table_id=self.table_id,
            name=self.name,
            columns=self._columns,
            constraints=self._constraints,
            indexes=self._indexes,
        )
