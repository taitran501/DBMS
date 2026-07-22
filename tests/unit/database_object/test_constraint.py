from dbms.database_object.constraint import (
    Constraint,
    ConstraintStrategy,
    ForeignKeyStrategy,
    PrimaryKeyStrategy,
    UniqueStrategy,
)
from dbms.database_object.row import Row
from unittest.mock import Mock
import pytest


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


def test_validate_primary_key():
    # Every primary-key field must contain a non-NULL value.
    constraint = Constraint("pk1", "pk_users", "PRIMARY_KEY", Mock())

    assert constraint.validate_primary_key(Row("r1", {"id": 1}, "v1"), ("id",)) is True
    assert constraint.validate_primary_key(Row("r2", {"id": None}, "v1"), ("id",)) is False


def test_validate_unique():
    # A candidate is valid only when no stored row has the same key values.
    constraint = Constraint("uq1", "uq_email", "UNIQUE", Mock())
    existing_rows = [Row("r1", {"email": "ada@example.com"}, "v1")]

    assert constraint.validate_unique(
        Row("r2", {"email": "grace@example.com"}, "v1"),
        ("email",),
        existing_rows,
    ) is True
    assert constraint.validate_unique(
        Row("r3", {"email": "ada@example.com"}, "v1"),
        ("email",),
        existing_rows,
    ) is False


def test_validate_foreign_key():
    # Foreign-key validity is a membership check against referenced key values.
    constraint = Constraint("fk1", "fk_orders", "FOREIGN_KEY", Mock())
    row = Row("r1", {"customer_id": 2}, "v1")

    assert constraint.validate_foreign_key(row, "customer_id", {1, 2}) is True
    assert constraint.validate_foreign_key(row, "customer_id", {1}) is False


def test_cascade_delete():
    # Cascading removes matching children while preserving unrelated rows.
    constraint = Constraint("fk1", "fk_orders", "FOREIGN_KEY", Mock())
    child_rows = [
        Row("o1", {"customer_id": 1}, "v1"),
        Row("o2", {"customer_id": 2}, "v1"),
    ]

    deleted_ids = constraint.cascade_delete(1, child_rows, "customer_id")

    assert deleted_ids == ["o1"]
    assert [row.row_id for row in child_rows] == ["o2"]


def test_cascade_update():
    # Cascading changes the foreign key of every child that references the old key.
    constraint = Constraint("fk1", "fk_orders", "FOREIGN_KEY", Mock())
    child_rows = [Row("o1", {"customer_id": 1}, "v1")]

    updated_count = constraint.cascade_update(1, 10, child_rows, "customer_id")

    assert updated_count == 1
    assert child_rows[0].values["customer_id"] == 10


def test_constraint_delegates_to_injected_strategy():
    strategy = Mock(spec=ConstraintStrategy)
    strategy.validate.return_value = True
    constraint = Constraint("c1", "custom", "CUSTOM", strategy=strategy)
    row = Row("r1", {"value": 1}, "v1")
    existing_rows = [Row("r0", {"value": 0}, "v1")]

    assert constraint.validate_row(row, existing_rows=existing_rows) is True
    strategy.validate.assert_called_once_with(row, existing_rows=existing_rows)


def test_constraint_strategy_can_be_replaced():
    first_strategy = Mock(spec=ConstraintStrategy)
    second_strategy = Mock(spec=ConstraintStrategy)
    second_strategy.validate.return_value = False
    constraint = Constraint("c1", "custom", "CUSTOM", strategy=first_strategy)
    constraint.set_strategy(second_strategy)
    row = Row("r1", {"value": 1}, "v1")

    assert constraint.validate_row(row) is False
    second_strategy.validate.assert_called_once_with(row, existing_rows=())


def test_unconfigured_constraint_fails_validation_explicitly():
    constraint = Constraint("c1", "custom", "CUSTOM", object())

    with pytest.raises(RuntimeError, match="Constraint 'custom' has no validation strategy"):
        constraint.validate_row(Row("r1", {"value": 1}, "v1"))


def test_concrete_strategies_share_validate_contract():
    row = Row("r2", {"id": 1, "email": "new@example.com", "customer_id": 2}, "v1")
    existing_rows = [Row("r1", {"email": "old@example.com"}, "v1")]

    assert PrimaryKeyStrategy(("id",)).validate(row, existing_rows=existing_rows) is True
    assert UniqueStrategy(("email",)).validate(row, existing_rows=existing_rows) is True
    assert ForeignKeyStrategy("customer_id", {1, 2}).validate(
        row, existing_rows=existing_rows
    ) is True


def test_primary_key_strategy_rejects_duplicate_key():
    strategy = PrimaryKeyStrategy(("tenant_id", "id"))
    existing_rows = [Row("r1", {"tenant_id": 1, "id": 10}, "v1")]

    assert strategy.validate(
        Row("r2", {"tenant_id": 1, "id": 10}, "v1"),
        existing_rows=existing_rows,
    ) is False
