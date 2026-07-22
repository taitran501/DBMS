from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Set

from dbms.database_object.row import Row


class ConstraintStrategy(ABC):
    """Common Strategy contract for validating a row."""

    @abstractmethod
    def validate(self, row: Row, *, existing_rows: Iterable[Row] = ()) -> bool:
        """Return whether the candidate row satisfies this strategy."""


class CheckStrategy(ConstraintStrategy):
    """Evaluate a custom CHECK rule."""

    def __init__(self, validation_rule: Callable[[Row], bool]) -> None:
        self.validation_rule = validation_rule

    def validate(self, row: Row, *, existing_rows: Iterable[Row] = ()) -> bool:
        return bool(self.validation_rule(row))


class PrimaryKeyStrategy(ConstraintStrategy):
    """Require every primary-key column to contain a non-NULL value."""

    def __init__(self, key_columns: tuple[str, ...]) -> None:
        if not key_columns:
            raise ValueError("Primary key requires at least one column")
        self.key_columns = key_columns

    def validate(self, row: Row, *, existing_rows: Iterable[Row] = ()) -> bool:
        if any(row.values.get(column) is None for column in self.key_columns):
            return False
        return UniqueStrategy(self.key_columns).validate(
            row, existing_rows=existing_rows
        )


class UniqueStrategy(ConstraintStrategy):
    """Reject duplicate values across the configured key columns."""

    def __init__(self, key_columns: tuple[str, ...]) -> None:
        if not key_columns:
            raise ValueError("Unique constraint requires at least one column")
        self.key_columns = key_columns

    def validate(self, row: Row, *, existing_rows: Iterable[Row] = ()) -> bool:
        candidate_values = tuple(row.values.get(column) for column in self.key_columns)
        return all(
            existing.row_id == row.row_id
            or tuple(existing.values.get(column) for column in self.key_columns)
            != candidate_values
            for existing in existing_rows
        )


class ForeignKeyStrategy(ConstraintStrategy):
    """Require a local key value to exist in the referenced key set."""

    def __init__(
        self,
        foreign_key_column: str,
        referenced_keys: Set[object] | Callable[[], Set[object]],
    ) -> None:
        if not foreign_key_column:
            raise ValueError("Foreign key column cannot be empty")
        self.foreign_key_column = foreign_key_column
        self.referenced_keys = referenced_keys

    def validate(self, row: Row, *, existing_rows: Iterable[Row] = ()) -> bool:
        referenced_keys = (
            self.referenced_keys()
            if callable(self.referenced_keys)
            else self.referenced_keys
        )
        return row.values.get(self.foreign_key_column) in referenced_keys

    def cascade_delete(
        self,
        parent_key_value: object,
        child_rows: list[Row],
        foreign_key_column: str | None = None,
    ) -> list[str]:
        column = foreign_key_column or self.foreign_key_column
        deleted_ids: list[str] = []
        remaining_rows: list[Row] = []
        for child in child_rows:
            if child.values.get(column) == parent_key_value:
                deleted_ids.append(child.row_id)
            else:
                remaining_rows.append(child)
        child_rows[:] = remaining_rows
        return deleted_ids

    def cascade_update(
        self,
        old_key_value: object,
        new_key_value: object,
        child_rows: list[Row],
        foreign_key_column: str | None = None,
    ) -> int:
        column = foreign_key_column or self.foreign_key_column
        updated_count = 0
        for child in child_rows:
            if child.values.get(column) == old_key_value:
                child.values[column] = new_key_value
                updated_count += 1
        return updated_count


class Constraint:
    """Context that delegates row validation to an interchangeable strategy."""

    def __init__(
        self,
        constraint_id: str,
        name: str,
        constraint_type: str,
        validation_rule: object = None,
        *,
        strategy: ConstraintStrategy | None = None,
    ) -> None:
        self.constraint_id = constraint_id
        self.name = name
        self.constraint_type = constraint_type
        self.validation_rule = validation_rule
        self.strategy = strategy
        if self.strategy is None and callable(validation_rule):
            self.strategy = CheckStrategy(validation_rule)

    def set_strategy(self, strategy: ConstraintStrategy) -> None:
        self.strategy = strategy

    def validate_row(
        self, row: Row, *, existing_rows: Iterable[Row] = ()
    ) -> bool:
        if self.strategy is None:
            raise RuntimeError(
                f"Constraint '{self.name}' has no validation strategy"
            )
        return self.strategy.validate(row, existing_rows=existing_rows)

    # Compatibility wrappers for the original public API.
    def validate_primary_key(self, row: Row, key_columns: tuple[str, ...]) -> bool:
        return PrimaryKeyStrategy(key_columns).validate(row)

    def validate_unique(
        self,
        row: Row,
        key_columns: tuple[str, ...],
        existing_rows: list[Row],
    ) -> bool:
        return UniqueStrategy(key_columns).validate(row, existing_rows=existing_rows)

    def validate_foreign_key(
        self,
        row: Row,
        foreign_key_column: str,
        referenced_keys: Set[object],
    ) -> bool:
        return ForeignKeyStrategy(foreign_key_column, referenced_keys).validate(row)

    def cascade_delete(
        self,
        parent_key_value: object,
        child_rows: list[Row],
        foreign_key_column: str,
    ) -> list[str]:
        strategy = ForeignKeyStrategy(foreign_key_column, set())
        return strategy.cascade_delete(parent_key_value, child_rows)

    def cascade_update(
        self,
        old_key_value: object,
        new_key_value: object,
        child_rows: list[Row],
        foreign_key_column: str,
    ) -> int:
        strategy = ForeignKeyStrategy(foreign_key_column, set())
        return strategy.cascade_update(old_key_value, new_key_value, child_rows)
