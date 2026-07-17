from dbms.database_object.trigger import Trigger


def test_trigger_stores_name_event_table_and_callback():
    callback = lambda row: None
    trigger = Trigger("tr1", "INSERT", "users", callback)

    assert trigger.name == "tr1"
    assert trigger.event == "INSERT"
    assert trigger.table_name == "users"
    assert trigger.callback is callback


def test_trigger_exposes_fire_method():
    trigger = Trigger("tr1", "INSERT", "users", lambda row: None)

    assert callable(trigger.fire)
