from dbms.query_processing.query_validator import QueryValidator
from dbms.query_processing.statement import Statement


def test_query_validator_returns_placeholder_success():
    assert QueryValidator().validate(Statement("SELECT")) is True
