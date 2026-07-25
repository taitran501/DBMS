import pytest

from dbms.query_processing.ast_visitor import (
    PhysicalPlanGeneratorVisitor,
    ValidationVisitor,
)
from dbms.query_processing.execution_operator import ProjectOperator
from dbms.query_processing.sql_parser import SQLParser


@pytest.fixture
def catalog_schema():
    return {
        "users": ["id", "name", "age", "city"],
        "orders": ["order_id", "user_id", "amount"],
    }


@pytest.fixture
def db_records():
    return {
        "users": [
            {"id": 1, "name": "Alice", "age": 25, "city": "Hanoi"},
            {"id": 2, "name": "Bob", "age": 17, "city": "Danang"},
            {"id": 3, "name": "Charlie", "age": 30, "city": "Saigon"},
        ]
    }


def test_validation_visitor_validates_existing_table_and_columns(catalog_schema):
    # Arrange
    parser = SQLParser()
    ast = parser.parse_sql("SELECT id, name FROM users WHERE age >= 18")
    validator = ValidationVisitor(catalog_schema)

    # Act
    is_valid = ast.accept(validator)

    # Assert
    assert is_valid is True
    assert len(validator.errors) == 0


def test_validation_visitor_rejects_unknown_table(catalog_schema):
    # Arrange
    parser = SQLParser()
    ast = parser.parse_sql("SELECT id FROM unknown_table")
    validator = ValidationVisitor(catalog_schema)

    # Act
    is_valid = ast.accept(validator)

    # Assert
    assert is_valid is False
    assert "Unknown table 'unknown_table'" in validator.errors


def test_validation_visitor_rejects_unknown_column(catalog_schema):
    # Arrange
    parser = SQLParser()
    ast = parser.parse_sql("SELECT unknown_column FROM users WHERE age > 18")
    validator = ValidationVisitor(catalog_schema)

    # Act
    is_valid = ast.accept(validator)

    # Assert
    assert is_valid is False
    assert "Unknown projected column 'unknown_column' in table 'users'" in validator.errors


def test_plan_generator_visitor_constructs_execution_pipeline(db_records):
    # Arrange
    parser = SQLParser()
    ast = parser.parse_sql("SELECT name, age FROM users WHERE age >= 18")
    plan_generator = PhysicalPlanGeneratorVisitor(db_records)

    # Act
    pipeline = ast.accept(plan_generator)

    # Assert
    assert isinstance(pipeline, ProjectOperator)
    assert pipeline.columns == ["name", "age"]


def test_generated_execution_pipeline_executes_query_successfully(db_records):
    # Arrange
    parser = SQLParser()
    ast = parser.parse_sql("SELECT name, city FROM users WHERE age >= 18")
    plan_generator = PhysicalPlanGeneratorVisitor(db_records)
    pipeline = ast.accept(plan_generator)

    # Act
    results = list(pipeline)

    # Assert
    assert results == [
        {"name": "Alice", "city": "Hanoi"},
        {"name": "Charlie", "city": "Saigon"},
    ]
