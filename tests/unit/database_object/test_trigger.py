from dbms.database_object.trigger import Trigger
from dbms.database_object.exceptions import TriggerError
from unittest.mock import Mock

import pytest


def test_trigger_can_be_created():
    # Arrange
    callback = lambda row: None
    trigger = Trigger("tr1", "INSERT", "users", callback)

    # Assert
    assert trigger.name == "tr1"
    assert trigger.event == "INSERT"
    assert trigger.table_name == "users"
    assert trigger.callback is callback
    assert callable(trigger.fire)


def test_fire():
    # Arrange
    callback = Mock(return_value=True)
    trigger = Trigger("tr1", "INSERT", "users", callback)
    row = object()

    # Act
    result = trigger.fire(row)

    # Assert
    assert result is True
    callback.assert_called_once_with(row)


def test_fire_treats_none_callback_result_as_success():
    callback = Mock(return_value=None)
    trigger = Trigger("tr1", "INSERT", "users", callback)

    assert trigger.fire(object()) is True


def test_fire_wraps_callback_error():
    def failing_callback(row: object) -> None:
        raise RuntimeError("audit write failed")

    trigger = Trigger("tr1", "INSERT", "users", failing_callback)

    with pytest.raises(TriggerError, match="tr1"):
        trigger.fire(object())
