from dbms.query_processing.statement import Statement


def test_statement_stores_statement_type():
    statement = Statement("SELECT")

    assert statement.statement_type == "SELECT"
