from dbms.database_object.trigger_manager import TriggerManager
from dbms.database_object.trigger import Trigger
from dbms.database_object.exceptions import DuplicateTriggerError
from unittest.mock import Mock

import pytest


def test_trigger_manager_can_be_created():
    # Arrange
    triggers = {}
    manager = TriggerManager(triggers)

    # Assert
    assert manager.triggers is triggers
    assert callable(manager.create_trigger)
    assert callable(manager.drop_trigger)
    assert callable(manager.bind_event)
    assert callable(manager.execute_triggers)


def test_create_trigger():
    # Arrange
    manager = TriggerManager({})
    callback = Mock()

    # Act
    result = manager.create_trigger("tr1", "INSERT", "users", callback)

    # Assert
    assert isinstance(result, Trigger)
    assert result.name == "tr1"
    assert manager.triggers["INSERT"] == [result]


def test_drop_trigger():
    # Arrange
    trigger = Trigger("tr1", "INSERT", "users", Mock())
    manager = TriggerManager({"INSERT": [trigger]})

    # Act
    result = manager.drop_trigger("tr1")

    # Assert
    assert result is True
    assert manager.triggers["INSERT"] == []


def test_bind_event():
    # Arrange
    trigger = Trigger("tr1", "INSERT", "users", Mock())
    callback = Mock()
    manager = TriggerManager({"INSERT": [trigger]})

    # Act
    result = manager.bind_event("INSERT", callback)

    # Assert
    assert result is True
    assert trigger.callback is callback


def test_execute_triggers():
    # Arrange
    trigger = Mock(spec=Trigger)
    trigger.fire.return_value = True
    manager = TriggerManager({"INSERT": [trigger]})
    row = object()

    # Act
    result = manager.execute_triggers("INSERT", row)

    # Assert
    assert result is True
    trigger.fire.assert_called_once_with(row)


def test_create_trigger_rejects_duplicate_names_across_events():
    manager = TriggerManager({})
    manager.create_trigger("audit_change", "INSERT", "users", Mock())

    with pytest.raises(DuplicateTriggerError, match="audit_change"):
        manager.create_trigger("audit_change", "UPDATE", "users", Mock())


def test_execute_triggers_notifies_observers_in_registration_order():
    manager = TriggerManager({})
    calls: list[str] = []
    manager.create_trigger(
        "audit_change", "INSERT", "users", lambda row: calls.append("audit")
    )
    manager.create_trigger(
        "refresh_cache", "INSERT", "users", lambda row: calls.append("cache")
    )

    assert manager.execute_triggers("INSERT", {"id": 1}) is True
    assert calls == ["audit", "cache"]
