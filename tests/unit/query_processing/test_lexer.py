from dbms.query_processing.lexer import Lexer


def test_lexer_can_be_created():
    assert isinstance(Lexer(), Lexer)
