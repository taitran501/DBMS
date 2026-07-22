from __future__ import annotations

from typing import Any, Callable
from dbms.database_object.row import Row


class ConstraintStrategy:
    """Abstract Strategy interface for constraint validation."""

    def validate(self, row: Row, **kwargs: Any) -> bool:
        return True


class CheckStrategy(ConstraintStrategy):
    """Strategy for evaluating custom row validation rules (CHECK constraints)."""

    def validate(self, row: Row, validation_rule: Callable[[Row], bool] | None = None) -> bool:
        if callable(validation_rule):
            return bool(validation_rule(row))
        return True


class PrimaryKeyStrategy(ConstraintStrategy):
    """Strategy for validating Primary Key constraints (non-NULL requirement)."""

    def validate_primary_key(self, row: Row, key_columns: tuple[str, ...]) -> bool:
        for col in key_columns:
            val = row.values.get(col)
            if val is None:
                return False
        return True


class UniqueStrategy(ConstraintStrategy):
    """Strategy for validating Unique constraints against stored rows."""

    def validate_unique(self, row: Row, key_columns: tuple[str, ...], existing_rows: list[Row]) -> bool:
        candidate_vals = tuple(row.values.get(col) for col in key_columns)
        for existing in existing_rows:
            if existing.row_id == row.row_id:
                continue
            existing_vals = tuple(existing.values.get(col) for col in key_columns)
            if candidate_vals == existing_vals:
                return False
        return True


class ForeignKeyStrategy(ConstraintStrategy):
    """Strategy for validating Foreign Key constraints and handling cascading actions."""

    def validate_foreign_key(self, row: Row, foreign_key_col: str, referenced_keys: set) -> bool:
        val = row.values.get(foreign_key_col)
        return val in referenced_keys

    def cascade_delete(
        self, parent_key_value: object, child_rows: list[Row], foreign_key_col: str
    ) -> list[str]:
        deleted_ids: list[str] = []
        i = 0
        while i < len(child_rows):
            if child_rows[i].values.get(foreign_key_col) == parent_key_value:
                deleted_row = child_rows.pop(i)
                deleted_ids.append(deleted_row.row_id)
            else:
                i += 1
        return deleted_ids

    def cascade_update(
        self, old_key_value: object, new_key_value: object, child_rows: list[Row], foreign_key_col: str
    ) -> int:
        updated_count = 0
        for child in child_rows:
            if child.values.get(foreign_key_col) == old_key_value:
                child.values[foreign_key_col] = new_key_value
                updated_count += 1
        return updated_count


class Constraint:
    """Context class for constraint validation delegating to strategy objects."""

    def __init__(
        self, constraint_id: str, name: str, constraint_type: str, validation_rule: object
    ) -> None:
        self.constraint_id = constraint_id
        self.name = name
        self.constraint_type = constraint_type
        self.validation_rule = validation_rule

        # Concrete Strategies
        self._check_strategy = CheckStrategy()
        self._pk_strategy = PrimaryKeyStrategy()
        self._unique_strategy = UniqueStrategy()
        self._fk_strategy = ForeignKeyStrategy()

    def validate_row(self, row: Row) -> bool:
        if callable(self.validation_rule):
            return self._check_strategy.validate(row, self.validation_rule)
        return True

    def validate_primary_key(self, row: Row, key_columns: tuple[str, ...]) -> bool:
        return self._pk_strategy.validate_primary_key(row, key_columns)

    def validate_unique(self, row: Row, key_columns: tuple[str, ...], existing_rows: list[Row]) -> bool:
        return self._unique_strategy.validate_unique(row, key_columns, existing_rows)

    def validate_foreign_key(self, row: Row, foreign_key_col: str, referenced_keys: set) -> bool:
        return self._fk_strategy.validate_foreign_key(row, foreign_key_col, referenced_keys)

    def cascade_delete(
        self, parent_key_value: object, child_rows: list[Row], foreign_key_col: str
    ) -> list[str]:
        return self._fk_strategy.cascade_delete(parent_key_value, child_rows, foreign_key_col)

    def cascade_update(
        self, old_key_value: object, new_key_value: object, child_rows: list[Row], foreign_key_col: str
    ) -> int:
        return self._fk_strategy.cascade_update(old_key_value, new_key_value, child_rows, foreign_key_col)

