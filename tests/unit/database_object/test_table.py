from dbms.database_object.table import Table


def test_table_can_be_created():
    columns = []
    rows = {}
    constraints = []
    indexes = []
    table = Table("t1", "users", columns, 0, rows, constraints, indexes)

    assert table.table_id == "t1"
    assert table.name == "users"
    assert table.columns is columns
    assert table.row_count == 0
    assert table.rows is rows
    assert table.constraints is constraints
    assert table.indexes is indexes
    assert callable(table.insert)
    assert callable(table.update)
    assert callable(table.delete)
    assert callable(table.truncate)
    assert callable(table.check_key_exists)


def test_insert():
    pass


def test_update_table_row():
    pass


def test_delete():
    pass


def test_truncate():
    pass
