from abc import ABC, abstractmethod
from typing import Any, Iterator

from dbms.query_processing.ast import ASTNode


class ExecutionOperator(ABC, Iterator[dict[str, Any]]):
    """Abstract base class for physical execution operators implementing the Volcano Iterator pattern."""

    @abstractmethod
    def open(self) -> None:
        """Initialize the operator execution state and open child iterators."""
        pass

    @abstractmethod
    def next(self) -> dict[str, Any] | None:
        """Return the next row matching the operator execution logic, or None when stream ends."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close operator execution and release resources."""
        pass

    def __iter__(self) -> "ExecutionOperator":
        self.open()
        return self

    def __next__(self) -> dict[str, Any]:
        row = self.next()
        if row is None:
            self.close()
            raise StopIteration
        return row


class SeqScanOperator(ExecutionOperator):
    """Physical operator for sequential scanning of a row collection or table data source."""

    def __init__(self, records: list[dict[str, Any]], table_name: str = "") -> None:
        self.records = records
        self.table_name = table_name
        self._cursor = 0

    def open(self) -> None:
        self._cursor = 0

    def next(self) -> dict[str, Any] | None:
        if self._cursor >= len(self.records):
            return None
        row = self.records[self._cursor]
        self._cursor += 1
        return row

    def close(self) -> None:
        self._cursor = len(self.records)


class FilterOperator(ExecutionOperator):
    """Physical operator for filtering child stream rows using an Interpreter AST predicate."""

    def __init__(self, child: ExecutionOperator, predicate: ASTNode | None = None) -> None:
        self.child = child
        self.predicate = predicate

    def open(self) -> None:
        self.child.open()

    def next(self) -> dict[str, Any] | None:
        while True:
            row = self.child.next()
            if row is None:
                return None
            if self.predicate is None or bool(self.predicate.interpret(row)):
                return row

    def close(self) -> None:
        self.child.close()


class ProjectOperator(ExecutionOperator):
    """Physical operator for projecting specified target column attributes from child stream rows."""

    def __init__(self, child: ExecutionOperator, columns: list[str]) -> None:
        self.child = child
        self.columns = columns

    def open(self) -> None:
        self.child.open()

    def next(self) -> dict[str, Any] | None:
        row = self.child.next()
        if row is None:
            return None
        if "*" in self.columns or not self.columns:
            return dict(row)
        return {col: row[col] for col in self.columns if col in row}

    def close(self) -> None:
        self.child.close()
