import pytest

from dbms.query_processing.ast import (
    AST,
    BinaryOpNode,
    CreateTableNode,
    IdentifierNode,
    InsertNode,
    LiteralNode,
    SelectNode,
)
from dbms.query_processing.lexer import Lexer
from dbms.query_processing.sql_parser import SQLParser
from dbms.query_processing.token_type import TokenType


def test_lexer_tokenizes_select_query():
    # Arrange
    lexer = Lexer()
    sql = "SELECT id, name FROM users WHERE age > 18"

    # Act
    tokens = lexer.tokenize(sql)

    # Assert
    token_values = [t.value for t in tokens if t.token_type != TokenType.END_OF_INPUT]
    assert token_values == ["SELECT", "id", ",", "name", "FROM", "users", "WHERE", "age", ">", 18]


def test_parser_creates_select_ast():
    # Arrange
    parser = SQLParser()
    sql = "SELECT id, name FROM users WHERE age > 18"

    # Act
    ast = parser.parse_sql(sql)

    # Assert
    assert isinstance(ast, AST)
    assert isinstance(ast.root_node, SelectNode)
    select_node: SelectNode = ast.root_node
    assert select_node.table_name == "users"
    assert select_node.columns == ["id", "name"]
    assert isinstance(select_node.where_clause, BinaryOpNode)


def test_parser_creates_insert_ast():
    # Arrange
    parser = SQLParser()
    sql = "INSERT INTO users VALUES (1, 'Alice')"

    # Act
    ast = parser.parse_sql(sql)

    # Assert
    assert isinstance(ast.root_node, InsertNode)
    insert_node: InsertNode = ast.root_node
    assert insert_node.table_name == "users"
    assert insert_node.values == [1, "Alice"]


def test_parser_creates_create_table_ast():
    # Arrange
    parser = SQLParser()
    sql = "CREATE TABLE users (id INT, name TEXT)"

    # Act
    ast = parser.parse_sql(sql)

    # Assert
    assert isinstance(ast.root_node, CreateTableNode)
    create_node: CreateTableNode = ast.root_node
    assert create_node.table_name == "users"
    assert create_node.columns == [("id", "INT"), ("name", "TEXT")]


def test_interpreter_evaluates_literal_node():
    # Arrange
    node = LiteralNode(42)

    # Act
    result = node.interpret()

    # Assert
    assert result == 42


def test_interpreter_evaluates_identifier_node():
    # Arrange
    node = IdentifierNode("age")
    context = {"id": 1, "age": 25, "name": "Bob"}

    # Act
    result = node.interpret(context)

    # Assert
    assert result == 25


def test_interpreter_evaluates_binary_operator_node():
    # Arrange
    left = IdentifierNode("age")
    right = LiteralNode(18)
    expr = BinaryOpNode(left, ">", right)

    # Act & Assert
    assert expr.interpret({"age": 25}) is True
    assert expr.interpret({"age": 15}) is False


def test_interpreter_evaluates_where_clause_context():
    # Arrange
    parser = SQLParser()
    sql = "SELECT id, name FROM users WHERE age >= 21"
    ast = parser.parse_sql(sql)

    # Act & Assert
    assert ast.interpret({"age": 25}) is True
    assert ast.interpret({"age": 18}) is False
