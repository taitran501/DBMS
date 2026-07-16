from dbms.database_object.trigger_manager import TriggerManager


def test_trigger_manager_can_be_created():
    assert isinstance(TriggerManager(), TriggerManager)
