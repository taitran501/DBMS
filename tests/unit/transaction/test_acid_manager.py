from dbms.transaction.acid_manager import AcidManager


def test_acid_manager_can_be_created():
    assert isinstance(AcidManager(), AcidManager)
