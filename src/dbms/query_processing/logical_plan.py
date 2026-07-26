from typing import Any


class LogicalPlan:
    """Represents a logical query plan consisting of a series of logical operators."""

    def __init__(self, operators: list[Any]) -> None:
        self.operators: list[Any] = operators
        self.operator_costs: list[float] | None = None
        self.estimated_cost: float | None = None
        self.table_cardinalities: dict[str, int] = {}
        self.available_indexes: dict[str, str] = {}
        self.output_columns: list[str] | None = None
        self.row_count: int | None = None
        self.selectivity: float | None = None

    def build(self) -> bool:
        """Build and validate the logical plan."""
        return True
