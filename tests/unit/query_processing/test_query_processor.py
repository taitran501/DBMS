from dbms.query_processing.query_processor import QueryProcessor
from dbms.query_processing.sql_parser import SQLParser
from dbms.query_processing.query_validator import QueryValidator
from dbms.query_processing.query_executor import QueryExecutor
from unittest.mock import Mock
import pytest

def test_query_processor_can_be_created():
    parser = SQLParser()
    validator = QueryValidator()
    executor = QueryExecutor()
    assert isinstance(QueryProcessor(parser, validator, executor), QueryProcessor)

def test_query_processor_stores_dependencies():
    parser = SQLParser()
    validator = QueryValidator()
    executor = QueryExecutor()
    processor = QueryProcessor(parser, validator, executor)

    assert processor.sql_parser is parser
    assert processor.query_validator is validator
    assert processor.query_executor is executor


def test_query_processor_runs_select_pipeline():
    processor = QueryProcessor(SQLParser(), QueryValidator(), QueryExecutor())
    session = {
        "data_sources": {
            "users": [
                {"id": 1, "name": "Ada", "age": 17},
                {"id": 2, "name": "Grace", "age": 21},
            ]
        },
        "schema_catalog": {"users": ["id", "name", "age"]},
        "username": "analyst",
        "user_permissions": {"analyst": {"SELECT"}},
    }

    result = processor.process("SELECT name FROM users WHERE age >= 18", session)

    assert result == [{"name": "Grace"}]


def test_query_processor_stops_before_execution_when_validation_fails():
    executor = Mock(spec=QueryExecutor)
    processor = QueryProcessor(SQLParser(), QueryValidator(), executor)
    session = {
        "data_sources": {"users": [{"id": 1, "name": "Ada"}]},
        "schema_catalog": {"users": ["id", "name"]},
        "username": "guest",
        "user_permissions": {"guest": set()},
    }

    with pytest.raises(ValueError, match="Query validation failed"):
        processor.process("SELECT name FROM users", session)

    executor.execute.assert_not_called()
