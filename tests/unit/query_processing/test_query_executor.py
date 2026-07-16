from dbms.query_processing.query_executor import QueryExecutor


def test_query_executor_can_be_created():
    assert isinstance(QueryExecutor(), QueryExecutor)
