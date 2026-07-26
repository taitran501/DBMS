import pytest

from dbms.query_processing.ast import AST, BinaryOpNode, IdentifierNode, LiteralNode, SelectNode
from dbms.query_processing.query_validator import (
    PermissionValidationHandler,
    QueryValidator,
    SchemaValidationHandler,
    SyntaxValidationHandler,
)


@pytest.fixture
def catalog_schema():
    return {
        "users": ["id", "name", "age", "city"],
        "orders": ["order_id", "user_id", "amount"],
    }


@pytest.fixture
def user_permissions():
    return {
        "alice": {"SELECT", "INSERT"},
        "bob": {"SELECT"},
        "guest": set(),
    }


def test_query_validator_can_be_created():
    validator = QueryValidator()
    assert isinstance(validator, QueryValidator)
    assert isinstance(validator.handler, SyntaxValidationHandler)


def test_query_validator_passes_valid_query(catalog_schema, user_permissions):
    # Arrange
    ast = AST(
        SelectNode(
            table_name="users",
            columns=["id", "name"],
            where_clause=BinaryOpNode(IdentifierNode("age"), ">=", LiteralNode(18)),
        )
    )
    context = {
        "schema_catalog": catalog_schema,
        "user_permissions": user_permissions,
        "username": "alice",
    }
    validator = QueryValidator()

    # Act
    is_valid = validator.validate(ast, context)

    # Assert
    assert is_valid is True
    assert len(validator.errors) == 0


def test_syntax_validation_handler_rejects_empty_ast():
    # Arrange
    validator = QueryValidator(handler=SyntaxValidationHandler())

    # Act
    is_valid = validator.validate(None)

    # Assert
    assert is_valid is False
    assert "Syntax error: AST statement is None" in validator.errors


def test_syntax_validation_handler_rejects_missing_table():
    # Arrange
    ast = AST(SelectNode(table_name="", columns=["id"]))
    validator = QueryValidator(handler=SyntaxValidationHandler())

    # Act
    is_valid = validator.validate(ast)

    # Assert
    assert is_valid is False
    assert "Syntax error: SELECT statement missing valid table name" in validator.errors


def test_schema_validation_handler_rejects_unknown_table(catalog_schema):
    # Arrange
    ast = AST(SelectNode(table_name="unknown_table", columns=["id"]))
    context = {"schema_catalog": catalog_schema}
    validator = QueryValidator(handler=SchemaValidationHandler())

    # Act
    is_valid = validator.validate(ast, context)

    # Assert
    assert is_valid is False
    assert "Unknown table 'unknown_table'" in validator.errors


def test_permission_validation_handler_rejects_unauthorized_user(user_permissions):
    # Arrange
    ast = AST(SelectNode(table_name="users", columns=["id"]))
    context = {
        "user_permissions": user_permissions,
        "username": "guest",
    }
    validator = QueryValidator(handler=PermissionValidationHandler())

    # Act
    is_valid = validator.validate(ast, context)

    # Assert
    assert is_valid is False
    assert "Permission error: User 'guest' denied 'SELECT' permission on table 'users'" in validator.errors


def test_custom_validation_chain(catalog_schema, user_permissions):
    # Arrange
    syntax_h = SyntaxValidationHandler()
    schema_h = SchemaValidationHandler()
    perm_h = PermissionValidationHandler()

    syntax_h.set_next(schema_h).set_next(perm_h)

    validator = QueryValidator(handler=syntax_h)

    # Act 1: Invalid syntax fails at first handler
    assert validator.validate(None) is False
    assert len(validator.errors) == 1

    # Act 2: Invalid schema fails at second handler
    ast_bad_schema = AST(SelectNode(table_name="missing_table", columns=["id"]))
    assert validator.validate(ast_bad_schema, {"schema_catalog": catalog_schema}) is False

    # Act 3: Valid query passes full chain
    ast_valid = AST(SelectNode(table_name="users", columns=["id"]))
    ctx_valid = {
        "schema_catalog": catalog_schema,
        "user_permissions": user_permissions,
        "username": "bob",
    }
    assert validator.validate(ast_valid, ctx_valid) is True
