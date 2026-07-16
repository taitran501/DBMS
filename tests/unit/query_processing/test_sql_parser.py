from dbms.query_processing.sql_parser import SqlParser
from dbms.query_processing.token import Token
from dbms.query_processing.token_type import TokenType


def test_sql_parser_returns_placeholder_statement():
    tokens = [Token(TokenType.END_OF_INPUT, "", 0)]

    assert SqlParser().parse(tokens) is None
