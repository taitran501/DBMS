from dbms.database_object.trigger import Trigger
from unittest.mock import Mock


def test_trigger_can_be_created():
    callback = lambda row: None
    trigger = Trigger("tr1", "INSERT", "users", callback)

    assert trigger.name == "tr1"
    assert trigger.event == "INSERT"
    assert trigger.table_name == "users"
    assert trigger.callback is callback
    assert callable(trigger.fire)


def test_fire():
    callback = Mock(return_value=True)
    trigger = Trigger("tr1", "INSERT", "users", callback)
    row = object()

    result = trigger.fire(row)

    assert result is True
    callback.assert_called_once_with(row)
