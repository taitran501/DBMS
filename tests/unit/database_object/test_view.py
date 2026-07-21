from dbms.database_object.view import View
from unittest.mock import Mock


def test_view_can_be_created():
    # Arrange
    query_executor = object()
    cached_results = []
    view = View("v1", "active_users", "SELECT * FROM users", query_executor, cached_results)

    # Assert
    assert view.view_id == "v1"
    assert view.name == "active_users"
    assert view.query_definition == "SELECT * FROM users"
    assert view.query_executor is query_executor
    assert view.cached_results is cached_results
    assert callable(view.refresh)


def test_refresh_success():
    # Arrange
    query_executor = Mock()
    results = [{"id": 1}]
    query_executor.execute.return_value = results
    view = View("v1", "active_users", "SELECT * FROM users", query_executor, [])

    # Act
    result = view.refresh()

    # Assert
    assert result is True
    assert view.cached_results is results
    query_executor.execute.assert_called_once_with("SELECT * FROM users")


def test_refresh_failure():
    # Arrange
    query_executor = Mock()
    query_executor.execute.side_effect = Exception("Query Failed")
    view = View("v1", "active_users", "SELECT * FROM invalid_table", query_executor, [{"old": "data"}])

    # Act
    result = view.refresh()

    # Assert
    assert result is False
    assert view.cached_results == [{"old": "data"}]  # Keeps old data on failure
    query_executor.execute.assert_called_once_with("SELECT * FROM invalid_table")


def test_validate_definition_valid():
    # Arrange
    query_executor = Mock()
    sql_parser = Mock()
    ast = Mock()
    ast.statement_type = "SELECT"
    sql_parser.parse.return_value = ast
    view = View("v1", "active_users", "SELECT * FROM users", query_executor, [])

    # Act
    result = view.validate_definition(sql_parser)

    # Assert
    assert result is True
    sql_parser.parse.assert_called_once_with("SELECT * FROM users")


def test_validate_definition_invalid_type():
    # Arrange
    query_executor = Mock()
    sql_parser = Mock()
    ast = Mock()
    ast.statement_type = "INSERT" # A view cannot be an insert statement
    sql_parser.parse.return_value = ast
    view = View("v1", "active_users", "INSERT INTO users VALUES(1)", query_executor, [])

    # Act
    result = view.validate_definition(sql_parser)

    # Assert
    assert result is False
    sql_parser.parse.assert_called_once_with("INSERT INTO users VALUES(1)")


def test_validate_definition_parse_error():
    # Arrange
    query_executor = Mock()
    sql_parser = Mock()
    sql_parser.parse.side_effect = Exception("Syntax error")
    view = View("v1", "active_users", "INVALID SQL", query_executor, [])

    # Act
    result = view.validate_definition(sql_parser)

    # Assert
    assert result is False
    sql_parser.parse.assert_called_once_with("INVALID SQL")


def test_resolve_dependencies():
    # Basic stub test for dependency resolution
    query_executor = Mock()
    catalog_manager = Mock()
    view = View("v1", "active_users", "SELECT * FROM users", query_executor, [])
    
    # Act
    result = view.resolve_dependencies(catalog_manager)
    
    # Assert
    assert result is True
