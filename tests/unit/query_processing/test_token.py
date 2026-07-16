from dbms.query_processing.token import Token
from dbms.query_processing.token_type import TokenType


def test_token_stores_type_value_and_position():
    token = Token(TokenType.KEYWORD, "SELECT", 0)

    assert token.token_type is TokenType.KEYWORD
    assert token.value == "SELECT"
    assert token.position == 0
