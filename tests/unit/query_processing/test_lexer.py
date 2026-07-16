from dbms.query_processing.lexer import Lexer


def test_lexer_returns_placeholder_token_list():
    assert Lexer().tokenize("SELECT 1") == []
