from dbms.query_processing.query_processor import QueryProcessor


def test_query_processor_can_be_created():
    assert isinstance(QueryProcessor(), QueryProcessor)
