from dbms.database_object.trigger import Trigger
from unittest.mock import Mock


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
