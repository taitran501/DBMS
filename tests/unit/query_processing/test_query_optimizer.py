from dbms.query_processing.query_optimizer import QueryOptimizer


def test_query_optimizer_can_be_created():
    assert isinstance(QueryOptimizer(), QueryOptimizer)
