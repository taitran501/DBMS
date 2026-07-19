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
