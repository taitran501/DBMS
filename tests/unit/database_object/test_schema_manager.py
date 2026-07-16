from dbms.database_object.schema_manager import SchemaManager

def test_create_schema():
    pass

def test_rename_schema():
    pass

def test_drop_schema():
    pass

def test_assign_owner():
    pass

def test_change_owner():
    pass

def test_reject_duplicate_schema():
    pass

def test_reject_unknown_schema():
    pass

def test_reject_dropping_nonempty_schema():
    pass

def test_schema_manager_can_be_created():
    assert isinstance(SchemaManager(), SchemaManager)
