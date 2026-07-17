from dbms.database_object.trigger_manager import TriggerManager
from dbms.database_object.trigger import Trigger
from unittest.mock import Mock


def test_trigger_manager_can_be_created():
    triggers = {}
    manager = TriggerManager(triggers)

    assert manager.triggers is triggers
    assert callable(manager.create_trigger)
    assert callable(manager.drop_trigger)
    assert callable(manager.bind_event)
    assert callable(manager.execute_triggers)


def test_create_trigger():
    manager = TriggerManager({})
    callback = Mock()

    result = manager.create_trigger("tr1", "INSERT", "users", callback)

    assert isinstance(result, Trigger)
    assert result.name == "tr1"
    assert manager.triggers["INSERT"] == [result]


def test_drop_trigger():
    trigger = Trigger("tr1", "INSERT", "users", Mock())
    manager = TriggerManager({"INSERT": [trigger]})

    result = manager.drop_trigger("tr1")

    assert result is True
    assert manager.triggers["INSERT"] == []


def test_bind_event():
    trigger = Trigger("tr1", "INSERT", "users", Mock())
    callback = Mock()
    manager = TriggerManager({"INSERT": [trigger]})

    result = manager.bind_event("INSERT", callback)

    assert result is True
    assert trigger.callback is callback


def test_execute_triggers():
    trigger = Mock(spec=Trigger)
    trigger.fire.return_value = True
    manager = TriggerManager({"INSERT": [trigger]})
    row = object()

    result = manager.execute_triggers("INSERT", row)

    assert result is True
    trigger.fire.assert_called_once_with(row)
