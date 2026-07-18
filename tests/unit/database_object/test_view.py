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


def test_refresh():
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
