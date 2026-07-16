from dbms.query_processing.select_statement import SelectStatement
from dbms.query_processing.statement import Statement


def test_select_statement_stores_basic_select_attributes():
    statement = SelectStatement("users", ["id", "name"])

    assert isinstance(statement, Statement)
    assert statement.statement_type == "SELECT"
    assert statement.table_name == "users"
    assert statement.columns == ["id", "name"]
    assert statement.where is None
