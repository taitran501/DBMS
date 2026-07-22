from __future__ import annotations

from dbms.database_object.column import Column
from dbms.database_object.constraint import Constraint
from dbms.database_object.data_type import DataType
from dbms.database_object.data_type_factory import DataTypeFactory
from dbms.database_object.index import Index
from dbms.database_object.table import Table


class TableBuilder:
    """Builder pattern implementation for constructing Table objects step-by-step."""

    _DATA_TYPE_CONVERTERS = {
        "INT": int,
        "INTEGER": int,
        "FLOAT": float,
        "REAL": float,
        "VARCHAR": str,
        "TEXT": str,
    }

    def __init__(self, name: str, table_id: str = "") -> None:
        if not name.strip():
            raise ValueError("Table name cannot be empty")
        self.name = name.strip()
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
        data_type: DataType | DataTypeFactory | str,
        column_id: str = "",
        nullable: bool = True,
    ) -> TableBuilder:
        if not name.strip():
            raise ValueError("Column name cannot be empty")

        name = name.strip()
        if any(col.name == name for col in self._columns):
            raise ValueError(f"Column '{name}' already exists in builder")

        if isinstance(data_type, DataTypeFactory):
            dt = data_type.create_data_type()
        elif isinstance(data_type, str):
            type_name = data_type.strip().upper()
            if not type_name:
                raise ValueError("Data type name cannot be empty")
            converter = self._DATA_TYPE_CONVERTERS.get(type_name, lambda value: value)
            dt = DataType(type_name, lambda value: True, converter)
        else:
            dt = data_type

        col_id = column_id or f"col_{len(self._columns) + 1}"
        col = Column(col_id, name, dt, nullable=nullable)
        self._columns.append(col)
        return self

    def add_column_object(self, column: Column) -> TableBuilder:
        if not isinstance(column, Column):
            raise TypeError("column must be a Column")
        if not column.name.strip():
            raise ValueError("Column name cannot be empty")
        if any(col.name == column.name for col in self._columns):
            raise ValueError(f"Column '{column.name}' already exists in builder")
        self._columns.append(column)
        return self

    def add_constraint(self, constraint: Constraint) -> TableBuilder:
        if not isinstance(constraint, Constraint):
            raise TypeError("constraint must be a Constraint")
        if not constraint.name.strip():
            raise ValueError("Constraint name cannot be empty")
        if any(
            existing.name == constraint.name
            or (
                constraint.constraint_id
                and existing.constraint_id == constraint.constraint_id
            )
            for existing in self._constraints
        ):
            raise ValueError(f"Constraint '{constraint.name}' already exists in builder")
        self._constraints.append(constraint)
        return self

    def add_index(self, index: Index) -> TableBuilder:
        if not isinstance(index, Index):
            raise TypeError("index must be an Index")
        if not index.name.strip():
            raise ValueError("Index name cannot be empty")
        if any(
            existing.name == index.name
            or (index.index_id and existing.index_id == index.index_id)
            for existing in self._indexes
        ):
            raise ValueError(f"Index '{index.name}' already exists in builder")
        self._indexes.append(index)
        return self

    def build(self) -> Table:
        self._validate()
        return Table(
            table_id=self.table_id,
            name=self.name,
            columns=list(self._columns),
            constraints=list(self._constraints),
            indexes=list(self._indexes),
        )

    def _validate(self) -> None:
        if len({column.name for column in self._columns}) != len(self._columns):
            raise ValueError("Table contains duplicate column names")
        if len({constraint.name for constraint in self._constraints}) != len(self._constraints):
            raise ValueError("Table contains duplicate constraint names")
        if len({index.name for index in self._indexes}) != len(self._indexes):
            raise ValueError("Table contains duplicate index names")
