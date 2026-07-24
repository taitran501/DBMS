from unittest.mock import Mock

import pytest

from dbms.database_object.dependencies import QueryExecutorProtocol
from dbms.database_object.view import View
from dbms.database_object.view_builder import ViewBuilder


def test_view_builder_can_be_created():
    # Arrange & Act
    builder = ViewBuilder("active_users", "SELECT * FROM users WHERE active = 1")

    # Assert
    assert builder is not None


def test_build_successful_view():
    # Arrange
    executor_mock = Mock(spec=QueryExecutorProtocol)
    builder = (
        ViewBuilder("active_users", "SELECT * FROM users WHERE active = 1")
        .set_view_id("v_001")
        .set_query_executor(executor_mock)
        .set_cached_results({"count": 10})
    )

    # Act
    view = builder.build()

    # Assert
    assert isinstance(view, View)
    assert view.view_id == "v_001"
    assert view.name == "active_users"
    assert view.query_definition == "SELECT * FROM users WHERE active = 1"
    assert view.query_executor == executor_mock
    assert view.cached_results == {"count": 10}


def test_build_with_default_view_id():
    # Arrange
    builder = ViewBuilder(
        name="sales_summary", query_definition="SELECT sum(amount) FROM sales"
    )

    # Act
    view = builder.build()

    # Assert
    assert isinstance(view, View)
    assert view.name == "sales_summary"
    assert view.view_id == "view_sales_summary"


def test_build_fails_when_name_empty():
    # Arrange
    builder = ViewBuilder("", "SELECT 1")

    # Act & Assert
    with pytest.raises(ValueError, match="View name cannot be empty"):
        builder.build()


def test_build_fails_when_query_definition_empty():
    # Arrange
    builder = ViewBuilder("v1", "")

    # Act & Assert
    with pytest.raises(ValueError, match="Query definition cannot be empty"):
        builder.build()


def test_builder_setters_mutate_and_return_self():
    # Arrange
    builder = ViewBuilder()

    # Act
    returned = (
        builder.set_name("my_view")
        .set_query_definition("SELECT * FROM t")
        .set_view_id("v123")
    )

    # Assert
    assert returned is builder
    view = builder.build()
    assert view.name == "my_view"
    assert view.query_definition == "SELECT * FROM t"
    assert view.view_id == "v123"
