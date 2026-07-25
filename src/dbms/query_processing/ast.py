from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from dbms.query_processing.ast_visitor import ASTVisitor


class ASTNode(ABC):
    """Abstract base class for Abstract Syntax Tree (AST) nodes implementing Interpreter & Visitor patterns."""

    @abstractmethod
    def interpret(self, context: dict[str, Any] | None = None) -> Any:
        """Evaluate / interpret the AST node within the provided data context."""
        pass

    @abstractmethod
    def accept(self, visitor: "ASTVisitor") -> Any:
        """Accept a visitor for double-dispatch AST traversal."""
        pass


class LiteralNode(ASTNode):
    """AST node representing literal constants (numbers, strings)."""

    def __init__(self, value: Any) -> None:
        self.value = value

    def interpret(self, context: dict[str, Any] | None = None) -> Any:
        return self.value

    def accept(self, visitor: "ASTVisitor") -> Any:
        return visitor.visit_literal(self)


class IdentifierNode(ASTNode):
    """AST node representing column or variable identifiers."""

    def __init__(self, name: str) -> None:
        self.name = name

    def interpret(self, context: dict[str, Any] | None = None) -> Any:
        if context is None:
            return None
        return context.get(self.name)

    def accept(self, visitor: "ASTVisitor") -> Any:
        return visitor.visit_identifier(self)


class BinaryOpNode(ASTNode):
    """AST node representing binary comparison and logical expressions (=, >, <, >=, <=, !=, AND, OR)."""

    def __init__(self, left: ASTNode, operator: str, right: ASTNode) -> None:
        self.left = left
        self.operator = operator
        self.right = right

    def interpret(self, context: dict[str, Any] | None = None) -> Any:
        left_val = self.left.interpret(context)
        right_val = self.right.interpret(context)

        if self.operator == "=":
            return left_val == right_val
        elif self.operator == "!=":
            return left_val != right_val
        elif self.operator == ">":
            return left_val > right_val if left_val is not None and right_val is not None else False
        elif self.operator == "<":
            return left_val < right_val if left_val is not None and right_val is not None else False
        elif self.operator == ">=":
            return left_val >= right_val if left_val is not None and right_val is not None else False
        elif self.operator == "<=":
            return left_val <= right_val if left_val is not None and right_val is not None else False
        elif self.operator.upper() == "AND":
            return bool(left_val and right_val)
        elif self.operator.upper() == "OR":
            return bool(left_val or right_val)
        else:
            raise ValueError(f"Unsupported binary operator: {self.operator}")

    def accept(self, visitor: "ASTVisitor") -> Any:
        return visitor.visit_binary_op(self)


class SelectNode(ASTNode):
    """AST node representing a SELECT query."""

    def __init__(
        self,
        table_name: str,
        columns: list[str],
        where_clause: ASTNode | None = None,
    ) -> None:
        self.table_name = table_name
        self.columns = columns
        self.where_clause = where_clause

    def interpret(self, context: dict[str, Any] | None = None) -> Any:
        if self.where_clause is None:
            return True
        return self.where_clause.interpret(context)

    def accept(self, visitor: "ASTVisitor") -> Any:
        return visitor.visit_select(self)


class InsertNode(ASTNode):
    """AST node representing an INSERT statement."""

    def __init__(self, table_name: str, values: list[Any]) -> None:
        self.table_name = table_name
        self.values = values

    def interpret(self, context: dict[str, Any] | None = None) -> Any:
        return {"table_name": self.table_name, "values": self.values}

    def accept(self, visitor: "ASTVisitor") -> Any:
        return visitor.visit_insert(self)


class CreateTableNode(ASTNode):
    """AST node representing a CREATE TABLE statement."""

    def __init__(self, table_name: str, columns: list[tuple[str, str]]) -> None:
        self.table_name = table_name
        self.columns = columns  # list of (column_name, data_type)

    def interpret(self, context: dict[str, Any] | None = None) -> Any:
        return {"table_name": self.table_name, "columns": self.columns}

    def accept(self, visitor: "ASTVisitor") -> Any:
        return visitor.visit_create_table(self)


class AST:
    """Abstract Syntax Tree container holding the root ASTNode."""

    def __init__(self, root_node: ASTNode) -> None:
        self.root_node = root_node

    def interpret(self, context: dict[str, Any] | None = None) -> Any:
        return self.root_node.interpret(context)

    def accept(self, visitor: "ASTVisitor") -> Any:
        """Accept a visitor at the root AST node."""
        return self.root_node.accept(visitor)

    def traverse(self) -> list[ASTNode]:
        """Return a list of all AST nodes via pre-order traversal."""
        nodes: list[ASTNode] = []

        def _visit(node: ASTNode) -> None:
            nodes.append(node)
            if isinstance(node, BinaryOpNode):
                _visit(node.left)
                _visit(node.right)
            elif isinstance(node, SelectNode) and node.where_clause:
                _visit(node.where_clause)

        _visit(self.root_node)
        return nodes
