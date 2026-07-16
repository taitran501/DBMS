from dbms.database_object.constraint_manager import ConstraintManager


def test_constraint_manager_can_be_created():
    assert isinstance(ConstraintManager(), ConstraintManager)
