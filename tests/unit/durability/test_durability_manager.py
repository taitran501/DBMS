from dbms.durability.durability_manager import DurabilityManager


def test_durability_manager_can_be_created():
    assert isinstance(DurabilityManager(), DurabilityManager)
