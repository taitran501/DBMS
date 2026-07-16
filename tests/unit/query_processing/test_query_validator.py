from dbms.query_processing.query_validator import QueryValidator


def test_query_validator_can_be_created():
    assert isinstance(QueryValidator(), QueryValidator)
