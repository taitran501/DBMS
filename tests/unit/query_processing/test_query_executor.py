from dbms.query_processing.query_executor import QueryExecutor
from dbms.query_processing.statement import Statement


def test_query_executor_returns_placeholder_result():
    assert QueryExecutor().execute(Statement("SELECT")) is None
