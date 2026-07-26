from typing import Any


class PhysicalPlan:
    """Represents an executable physical query plan consisting of physical execution operators."""

    def __init__(
        self,
        operators: list[Any],
        output_columns: list[str] | None = None,
        cost: float | None = None,
    ) -> None:
        self.operators: list[Any] = operators
        self.output_columns: list[str] | None = output_columns
        self.cost: float | None = cost

    def generate(self) -> bool:
        """Generate the executable physical execution structure."""
        return True
