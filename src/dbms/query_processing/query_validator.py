from abc import ABC, abstractmethod
from typing import Any

from dbms.query_processing.ast import (
    AST,
    ASTNode,
    CreateTableNode,
    InsertNode,
    SelectNode,
)
from dbms.query_processing.ast_visitor import ValidationVisitor
from dbms.query_processing.statement import Statement


class ValidationHandler(ABC):
    """Abstract base class for Chain of Responsibility query validation handlers."""

    def __init__(self, next_handler: "ValidationHandler | None" = None) -> None:
        self.next_handler: ValidationHandler | None = next_handler

    def set_next(self, handler: "ValidationHandler") -> "ValidationHandler":
        """Link the next validation handler in the chain and return it for chaining."""
        self.next_handler = handler
        return handler

    def validate(
        self,
        ast: AST,
        context: dict[str, Any] | None = None,
        errors: list[str] | None = None,
    ) -> bool:
        """Validate the request and delegate to the next handler if successful."""
        if errors is None:
            errors = []

        if not self._validate_current(ast, context, errors):
            return False

        if self.next_handler is not None:
            return self.next_handler.validate(ast, context, errors)

        return True

    @abstractmethod
    def _validate_current(
        self,
        ast: AST,
        context: dict[str, Any] | None,
        errors: list[str],
    ) -> bool:
        """Perform validation logic for this specific handler."""
        pass


class SyntaxValidationHandler(ValidationHandler):
    """Handler verifying AST node non-nullness and fundamental syntax rules."""

    def _validate_current(
        self,
        ast: AST,
        context: dict[str, Any] | None,
        errors: list[str],
    ) -> bool:
        if ast is None:
            errors.append("Syntax error: AST is None")
            return False

        root = ast.root_node

        if isinstance(root, SelectNode):
            if not root.table_name or not isinstance(root.table_name, str):
                errors.append("Syntax error: SELECT statement missing valid table name")
                return False
            if not root.columns or len(root.columns) == 0:
                errors.append("Syntax error: SELECT statement missing columns")
                return False
        elif isinstance(root, InsertNode):
            if not root.table_name or not isinstance(root.table_name, str):
                errors.append("Syntax error: INSERT statement missing valid table name")
                return False
            if root.values is None or not isinstance(root.values, list):
                errors.append("Syntax error: INSERT statement missing values list")
                return False
        elif isinstance(root, CreateTableNode):
            if not root.table_name or not isinstance(root.table_name, str):
                errors.append("Syntax error: CREATE TABLE statement missing valid table name")
                return False
            if not root.columns or len(root.columns) == 0:
                errors.append("Syntax error: CREATE TABLE statement missing column definitions")
                return False

        return True


class SchemaValidationHandler(ValidationHandler):
    """Handler checking table and column identifiers against catalog schema metadata."""

    def _validate_current(
        self,
        ast: AST,
        context: dict[str, Any] | None,
        errors: list[str],
    ) -> bool:
        if context is None or "schema_catalog" not in context:
            return True

        schema_catalog = context["schema_catalog"]
        visitor = ValidationVisitor(schema_catalog)

        is_valid = ast.accept(visitor)
        if not is_valid:
            errors.extend(visitor.errors)
            return False

        return True


class PermissionValidationHandler(ValidationHandler):
    """Handler verifying user operational permissions against requested target tables."""

    def _validate_current(
        self,
        ast: AST,
        context: dict[str, Any] | None,
        errors: list[str],
    ) -> bool:
        if context is None or "user_permissions" not in context:
            return True

        user_permissions: dict[str, set[str]] = context["user_permissions"]
        username = context.get("username", "guest")
        allowed_permissions = user_permissions.get(username, set())

        root = ast.root_node
        required_action = "SELECT"
        target_table = getattr(root, "table_name", None)

        if isinstance(root, SelectNode):
            required_action = "SELECT"
        elif isinstance(root, InsertNode):
            required_action = "INSERT"
        elif isinstance(root, CreateTableNode):
            required_action = "CREATE"

        # Check action permission globally or per-table format ("table:ACTION" or "ACTION")
        has_permission = (
            required_action in allowed_permissions
            or f"{target_table}:{required_action}" in allowed_permissions
            or "*" in allowed_permissions
        )

        if not has_permission:
            errors.append(
                f"Permission error: User '{username}' denied '{required_action}' permission on table '{target_table}'"
            )
            return False

        return True


class QueryValidator:
    """Validator context executing a Chain of Responsibility validation pipeline."""

    def __init__(self, handler: ValidationHandler | None = None) -> None:
        if handler is not None:
            self.handler = handler
        else:
            # Construct default chain: Syntax -> Schema -> Permission
            syntax_h = SyntaxValidationHandler()
            schema_h = SchemaValidationHandler()
            perm_h = PermissionValidationHandler()

            syntax_h.set_next(schema_h).set_next(perm_h)
            self.handler = syntax_h

        self.errors: list[str] = []

    def set_handler(self, handler: ValidationHandler) -> None:
        """Replace the root validation handler in the validator context."""
        self.handler = handler

    def validate(
        self,
        ast: AST,
        context: dict[str, Any] | None = None,
    ) -> bool:
        """Execute the validation chain on the given AST."""
        self.errors.clear()
        return self.handler.validate(ast, context, self.errors)
