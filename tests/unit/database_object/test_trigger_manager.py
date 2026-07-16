from dbms.database_object.trigger_manager import TriggerManager

def test_create_trigger():
    pass

def test_drop_trigger():
    pass

def test_bind_event():
    pass

def test_execute_trigger():
    pass

def test_skip_unmatched_event():
    pass

def test_abort_on_trigger_failure():
    pass

def test_reject_duplicate_trigger():
    pass

def test_trigger_manager_can_be_created():
    assert isinstance(TriggerManager(), TriggerManager)
