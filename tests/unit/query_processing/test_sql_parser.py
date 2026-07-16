from dbms.query_processing.sql_parser import SqlParser


def test_sql_parser_can_be_created():
    assert isinstance(SqlParser(), SqlParser)
