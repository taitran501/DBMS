from abc import ABC, abstractmethod
from typing import Any

from dbms.query_processing.ast import (
    BinaryOpNode,
    CreateTableNode,
    IdentifierNode,
    InsertNode,
    LiteralNode,
    SelectNode,
)
from dbms.query_processing.execution_operator import (
    ExecutionOperator,
    FilterOperator,
    ProjectOperator,
    SeqScanOperator,
)


class ASTVisitor(ABC):
    """Abstract Visitor class defining visit methods for AST nodes."""

    @abstractmethod
    def visit_literal(self, node: LiteralNode) -> Any:
        pass

    @abstractmethod
    def visit_identifier(self, node: IdentifierNode) -> Any:
        pass

    @abstractmethod
    def visit_binary_op(self, node: BinaryOpNode) -> Any:
        pass

    @abstractmethod
    def visit_select(self, node: SelectNode) -> Any:
        pass

    @abstractmethod
    def visit_insert(self, node: InsertNode) -> Any:
        pass

    @abstractmethod
    def visit_create_table(self, node: CreateTableNode) -> Any:
        pass


class ValidationVisitor(ASTVisitor):
    """Concrete visitor that validates referenced table names and column names against catalog schemas."""

    def __init__(self, schema_catalog: dict[str, list[str]]) -> None:
        # schema_catalog format e.g.: {"users": ["id", "name", "age", "city"]}
        self.schema_catalog = schema_catalog
        self.errors: list[str] = []
        self._current_table: str | None = None

    def visit_literal(self, node: LiteralNode) -> Any:
        return True

    def visit_identifier(self, node: IdentifierNode) -> Any:
        if self._current_table and self._current_table in self.schema_catalog:
            valid_cols = self.schema_catalog[self._current_table]
            if node.name not in valid_cols:
                self.errors.append(f"Unknown column '{node.name}' in table '{self._current_table}'")
                return False
        return True

    def visit_binary_op(self, node: BinaryOpNode) -> Any:
        left_valid = node.left.accept(self)
        right_valid = node.right.accept(self)
        return left_valid and right_valid

    def visit_select(self, node: SelectNode) -> Any:
        if node.table_name not in self.schema_catalog:
            self.errors.append(f"Unknown table '{node.table_name}'")
            return False

        self._current_table = node.table_name
        valid_cols = self.schema_catalog[node.table_name]

        for col in node.columns:
            if col != "*" and col not in valid_cols:
                self.errors.append(f"Unknown projected column '{col}' in table '{node.table_name}'")

        if node.where_clause:
            node.where_clause.accept(self)

        return len(self.errors) == 0

    def visit_insert(self, node: InsertNode) -> Any:
        if node.table_name not in self.schema_catalog:
            self.errors.append(f"Unknown table '{node.table_name}'")
            return False
        return True

    def visit_create_table(self, node: CreateTableNode) -> Any:
        return True


class PhysicalPlanGeneratorVisitor(ASTVisitor):
    """Concrete visitor that constructs an ExecutionOperator pipeline from a SelectNode AST."""

    def __init__(self, data_sources: dict[str, list[dict[str, Any]]]) -> None:
        # data_sources format e.g.: {"users": [{"id": 1, ...}, ...]}
        self.data_sources = data_sources

    def visit_literal(self, node: LiteralNode) -> Any:
        return node.value

    def visit_identifier(self, node: IdentifierNode) -> Any:
        return node.name

    def visit_binary_op(self, node: BinaryOpNode) -> Any:
        return node

    def visit_select(self, node: SelectNode) -> ExecutionOperator:
        records = self.data_sources.get(node.table_name, [])
        scan_op = SeqScanOperator(records, table_name=node.table_name)

        if node.where_clause:
            filter_op = FilterOperator(child=scan_op, predicate=node.where_clause)
            return ProjectOperator(child=filter_op, columns=node.columns)

        return ProjectOperator(child=scan_op, columns=node.columns)

    def visit_insert(self, node: InsertNode) -> Any:
        raise NotImplementedError("Insert execution plan generation not implemented in this visitor")

    def visit_create_table(self, node: CreateTableNode) -> Any:
        raise NotImplementedError("Create Table execution plan generation not implemented in this visitor")
