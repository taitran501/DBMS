from dbms.query_processing.query_processor import QueryProcessor
from dbms.query_processing.sql_parser import SqlParser
from dbms.query_processing.query_validator import QueryValidator
from dbms.query_processing.query_executor import QueryExecutor

def test_query_processor_can_be_created():
    parser = SqlParser()
    validator = QueryValidator()
    executor = QueryExecutor()
    assert isinstance(QueryProcessor(parser, validator, executor), QueryProcessor)

def test_query_processor_stores_dependencies_and_returns_placeholder():
    parser = SqlParser()
    validator = QueryValidator()
    executor = QueryExecutor()
    processor = QueryProcessor(parser, validator, executor)

    assert processor.sql_parser is parser
    assert processor.query_validator is validator
    assert processor.query_executor is executor
    assert processor.process("SELECT 1") is None
