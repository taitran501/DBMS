from dbms.database_object.view_manager import ViewManager

def test_create_view():
    pass

def test_drop_view():
    pass

def test_resolve_view_definition():
    pass

def test_track_view_dependency():
    pass

def test_reject_duplicate_view():
    pass

def test_reject_unknown_dependency():
    pass

def test_reject_dropping_referenced_view():
    pass

def test_view_manager_can_be_created():
    assert isinstance(ViewManager(), ViewManager)
