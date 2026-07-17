from dbms.database_object.constraint import Constraint


def test_constraint_can_be_created():
    validation_rule = lambda row: True
    constraint = Constraint("c1", "chk_age", "CHECK", validation_rule)

    assert constraint.constraint_id == "c1"
    assert constraint.name == "chk_age"
    assert constraint.constraint_type == "CHECK"
    assert constraint.validation_rule is validation_rule
    assert callable(constraint.validate_row)


def test_validate_row():
    pass
