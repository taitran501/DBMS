from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
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


class MutationOperator(ABC):
    """Executable command that changes the in-memory query session state."""

    @abstractmethod
    def execute(self) -> object:
        """Apply the mutation and return its command result."""
        pass


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


class IndexScanOperator(ExecutionOperator):
    """Selection scan chosen for an indexed predicate in the current in-memory runtime."""

    def __init__(
        self,
        records: list[dict[str, Any]],
        table_name: str,
        index_name: str,
        predicate: ASTNode,
    ) -> None:
        self.records = records
        self.table_name = table_name
        self.index_name = index_name
        self.predicate = predicate
        self._scan = SeqScanOperator(records, table_name)

    def open(self) -> None:
        self._scan.open()

    def next(self) -> dict[str, Any] | None:
        while (row := self._scan.next()) is not None:
            if bool(self.predicate.interpret(row)):
                return row
        return None

    def close(self) -> None:
        self._scan.close()


class ParallelTableScanOperator(ExecutionOperator):
    """Read table partitions concurrently while preserving source-row order."""

    def __init__(
        self,
        records: list[dict[str, Any]],
        table_name: str,
        worker_count: int = 2,
    ) -> None:
        self.records = records
        self.table_name = table_name
        self.worker_count = worker_count
        self._materialized_records: list[dict[str, Any]] = []
        self._cursor = 0

    def open(self) -> None:
        self._cursor = 0
        if not self.records:
            self._materialized_records = []
            return

        workers = min(self.worker_count, len(self.records))
        chunk_size = (len(self.records) + workers - 1) // workers
        chunks = [self.records[index : index + chunk_size] for index in range(0, len(self.records), chunk_size)]
        with ThreadPoolExecutor(max_workers=workers) as executor:
            partitions = list(executor.map(list, chunks))
        self._materialized_records = [row for partition in partitions for row in partition]

    def next(self) -> dict[str, Any] | None:
        if self._cursor >= len(self._materialized_records):
            return None
        row = self._materialized_records[self._cursor]
        self._cursor += 1
        return row

    def close(self) -> None:
        self._cursor = len(self._materialized_records)


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


class InsertOperator(MutationOperator):
    """Append a values-only INSERT row to a schema-backed in-memory table."""

    def __init__(
        self,
        data_sources: dict[str, list[dict[str, Any]]],
        schema_catalog: dict[str, list[str]],
        table_name: str,
        values: list[Any],
    ) -> None:
        self.data_sources = data_sources
        self.schema_catalog = schema_catalog
        self.table_name = table_name
        self.values = values

    def execute(self) -> int:
        if self.table_name not in self.data_sources:
            raise KeyError(f"Table '{self.table_name}' does not exist")

        columns = self.schema_catalog.get(self.table_name)
        if columns is None:
            raise KeyError(f"Schema for table '{self.table_name}' does not exist")
        if len(self.values) != len(columns):
            raise ValueError(
                f"INSERT into '{self.table_name}' expected {len(columns)} values, got {len(self.values)}"
            )

        self.data_sources[self.table_name].append(dict(zip(columns, self.values)))
        return 1


class CreateTableOperator(MutationOperator):
    """Create an empty table and its ordered schema in the in-memory query session."""

    def __init__(
        self,
        data_sources: dict[str, list[dict[str, Any]]],
        schema_catalog: dict[str, list[str]],
        table_name: str,
        columns: list[tuple[str, str]],
    ) -> None:
        self.data_sources = data_sources
        self.schema_catalog = schema_catalog
        self.table_name = table_name
        self.columns = columns

    def execute(self) -> bool:
        if self.table_name in self.data_sources or self.table_name in self.schema_catalog:
            raise ValueError(f"Table '{self.table_name}' already exists")

        self.data_sources[self.table_name] = []
        self.schema_catalog[self.table_name] = [name for name, _ in self.columns]
        return True
