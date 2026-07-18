from dbms.database_object.constraint import Constraint
from dbms.database_object.row import Row
from unittest.mock import Mock


def test_constraint_can_be_created():
    # Arrange
    validation_rule = lambda row: True
    constraint = Constraint("c1", "chk_age", "CHECK", validation_rule)

    # Assert
    assert constraint.constraint_id == "c1"
    assert constraint.name == "chk_age"
    assert constraint.constraint_type == "CHECK"
    assert constraint.validation_rule is validation_rule
    assert callable(constraint.validate_row)


def test_validate_row():
    # Arrange
    validation_rule = Mock(return_value=True)
    constraint = Constraint("c1", "chk_age", "CHECK", validation_rule)
    row = Row("r1", {"age": 25}, "v1")

    # Act
    result = constraint.validate_row(row)

    # Assert
    assert result is True
    validation_rule.assert_called_once_with(row)
