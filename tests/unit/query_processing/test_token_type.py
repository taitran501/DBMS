from dbms.query_processing.token_type import TokenType


def test_token_type_defines_core_sql_token_categories():
    assert TokenType.KEYWORD.name == "KEYWORD"
    assert TokenType.IDENTIFIER.name == "IDENTIFIER"
    assert TokenType.END_OF_INPUT.name == "END_OF_INPUT"
