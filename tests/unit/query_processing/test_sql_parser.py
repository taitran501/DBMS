import pytest

from dbms.query_processing.sql_parser import SQLParser


def test_parse():
    # Arrange
    sql = "SELECT id FROM users"

    # Act
    statement = SQLParser().parse(sql)

    # Assert
    assert statement.statement_type == "SELECT"

def test_parse_select():
    # Arrange
    sql = "SELECT id, name FROM users"

    # Act
    statement = SQLParser().parse(sql)

    # Assert
    # Parsing separates projected columns from the source table.
    assert statement.statement_type == "SELECT"
    assert statement.table_name == "users"
    assert statement.columns == ["id", "name"]

def test_parse_insert():
    # Arrange
    sql = "INSERT INTO users (id, name) VALUES (1, 'Alice')"

    # Act
    statement = SQLParser().parse(sql)

    # Assert
    # Column names are paired with their converted literal values.
    assert statement.statement_type == "INSERT"
    assert statement.table_name == "users"
    assert statement.values == {"id": 1, "name": "Alice"}

def test_parse_update():
    # Arrange
    sql = "UPDATE users SET name = 'Bob' WHERE id = 1"

    # Act
    statement = SQLParser().parse(sql)

    # Assert
    assert statement.statement_type == "UPDATE"
    assert statement.assignments == {"name": "Bob"}
    assert statement.where == "id = 1"

def test_parse_delete():
    # Arrange
    sql = "DELETE FROM users WHERE id = 1"

    # Act
    statement = SQLParser().parse(sql)

    # Assert
    assert statement.statement_type == "DELETE"
    assert statement.table_name == "users"
    assert statement.where == "id = 1"

def test_parse_expression():
    # Arrange
    sql = "age >= 18"

    # Act
    expression = SQLParser().parse_expression(sql)

    # Assert
    assert expression.left == "age"
    assert expression.operator == ">="
    assert expression.right == 18

def test_parse_where_clause():
    # Arrange
    sql = "WHERE active = true AND age >= 18"

    # Act
    where = SQLParser().parse_where_clause(sql)

    # Assert
    # AND keeps both predicates in the same filter tree.
    assert where.operator == "AND"
    assert len(where.predicates) == 2

def test_reject_incomplete_statement():
    # Arrange
    sql = "SELECT id FROM"

    # Act
    with pytest.raises(ValueError) as error:
        SQLParser().parse(sql)

    # Assert
    assert "incomplete" in str(error.value)

def test_reject_unexpected_token():
    # Arrange
    sql = "SELECT SELECT FROM users"

    # Act
    with pytest.raises(ValueError) as error:
        SQLParser().parse(sql)

    # Assert
    assert "unexpected" in str(error.value)

def test_sql_parser_can_be_created():
    # Arrange
    parser_type = SQLParser

    # Act
    parser = parser_type()

    # Assert
    assert isinstance(parser, SQLParser)


def test_parse_create_table():
    # Arrange
    sql = "CREATE TABLE users (id INT)"

    # Act
    statement = SQLParser().parse(sql)

    # Assert
    # A column definition preserves both its name and SQL type.
    assert statement.statement_type == "CREATE_TABLE"
    assert statement.table_name == "users"
    assert statement.columns == [("id", "INT")]

def test_parse_alter_table():
    # Arrange
    sql = "ALTER TABLE users ADD age INT"

    # Act
    statement = SQLParser().parse(sql)

    # Assert
    assert statement.statement_type == "ALTER_TABLE"
    assert statement.table_name == "users"
    assert statement.action == ("ADD", "age", "INT")

def test_parse_join():
    # Arrange
    sql = "SELECT users.id FROM users JOIN orders ON users.id = orders.user_id"

    # Act
    statement = SQLParser().parse(sql)

    # Assert
    # The join target and ON condition remain available to planning.
    assert statement.statement_type == "SELECT"
    assert statement.joins == [("orders", "users.id = orders.user_id")]

def test_parse_sub_query():
    # Arrange
    sql = "SELECT id FROM (SELECT id FROM users) AS active_users"

    # Act
    statement = SQLParser().parse(sql)

    # Assert
    # The nested SELECT remains a statement so later planning can optimize it.
    assert statement.source.alias == "active_users"
    assert statement.source.statement.statement_type == "SELECT"

def test_parse_cte():
    # Arrange
    sql = "WITH active_users AS (SELECT id FROM users) SELECT id FROM active_users"

    # Act
    statement = SQLParser().parse(sql)

    # Assert
    # A CTE keeps its name together with its parsed inner statement.
    assert statement.statement_type == "SELECT"
    assert statement.ctes[0].name == "active_users"
    assert statement.ctes[0].statement.statement_type == "SELECT"

def test_parse_window_function():
    # Arrange
    sql = "SELECT ROW_NUMBER() OVER (ORDER BY id) FROM users"

    # Act
    statement = SQLParser().parse(sql)

    # Assert
    # Window ordering belongs to the function, not the whole SELECT.
    assert statement.statement_type == "SELECT"
    assert statement.columns[0].function == "ROW_NUMBER"
    assert statement.columns[0].window.order_by == ["id"]
