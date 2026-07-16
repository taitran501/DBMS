from dbms.database_object.table_manager import TableManager

def test_create_table():
    pass

def test_rename_table():
    pass

def test_drop_table():
    pass

def test_reject_duplicate_table():
    pass

def test_reject_unknown_schema():
    pass

def test_require_at_least_one_column():
    pass

def test_reject_dropping_referenced_table():
    pass

def test_load_table_metadata():
    pass

def test_table_manager_can_be_created():
    assert isinstance(TableManager(), TableManager)
