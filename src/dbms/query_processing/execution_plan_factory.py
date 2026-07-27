import re
from abc import ABC, abstractmethod
from typing import Any

from dbms.query_processing.ast import ASTNode
from dbms.query_processing.execution_operator import (
    ExecutionOperator,
    FilterOperator,
    ProjectOperator,
    SeqScanOperator,
)


class UnknownOperatorError(Exception):
    """Raised when an unrecognized execution operator descriptor is provided."""

    pass


class ExecutionOperatorFactory(ABC):
    """Abstract Factory Method interface for creating physical ExecutionOperators."""

    @abstractmethod
    def create_operator(
        self,
        op_descriptor: str,
        data_sources: dict[str, list[dict]] | None = None,
        child: ExecutionOperator | None = None,
    ) -> ExecutionOperator:
        """Instantiate a physical ExecutionOperator from a descriptor string."""
        pass


class SeqScanOperatorFactory(ExecutionOperatorFactory):
    """Factory Method creator for SeqScanOperator physical iterator."""

    def create_operator(
        self,
        op_descriptor: str,
        data_sources: dict[str, list[dict]] | None = None,
        child: ExecutionOperator | None = None,
    ) -> ExecutionOperator:
        match = re.match(r"(?:TableScan|SequentialScan)\(([^)]+)\)", op_descriptor)
        if not match:
            raise UnknownOperatorError(f"Invalid scan operator descriptor: {op_descriptor}")
        table_name = match.group(1).split(":")[0].strip()
        data_sources = data_sources or {}
        records = data_sources.get(table_name, [])
        return SeqScanOperator(records=records, table_name=table_name)


class FilterOperatorFactory(ExecutionOperatorFactory):
    """Factory Method creator for FilterOperator physical iterator."""

    def create_operator(
        self,
        op_descriptor: str,
        data_sources: dict[str, list[dict]] | None = None,
        child: ExecutionOperator | None = None,
    ) -> ExecutionOperator:
        if not child:
            raise ValueError("FilterOperator requires a valid child ExecutionOperator.")
        match = re.match(r"Filter\(([^)]+)\)", op_descriptor)
        predicate: Any = match.group(1).strip() if match else None
        return FilterOperator(child=child, predicate=predicate)


class ProjectOperatorFactory(ExecutionOperatorFactory):
    """Factory Method creator for ProjectOperator physical iterator."""

    def create_operator(
        self,
        op_descriptor: str,
        data_sources: dict[str, list[dict]] | None = None,
        child: ExecutionOperator | None = None,
    ) -> ExecutionOperator:
        if not child:
            raise ValueError("ProjectOperator requires a valid child ExecutionOperator.")
        match = re.match(r"Project\(([^)]+)\)", op_descriptor)
        if not match:
            raise UnknownOperatorError(f"Invalid project descriptor: {op_descriptor}")
        cols = [c.strip() for c in match.group(1).split(",")]
        return ProjectOperator(child=child, columns=cols)


class ExecutionPlanFactory:
    """Coordinator Factory utilizing concrete ExecutionOperatorFactory creators to construct physical operator trees."""

    def __init__(self, data_sources: dict[str, list[dict]] | None = None) -> None:
        self.data_sources: dict[str, list[dict]] = data_sources or {}
        self._factories: dict[str, ExecutionOperatorFactory] = {
            "TableScan": SeqScanOperatorFactory(),
            "SequentialScan": SeqScanOperatorFactory(),
            "Filter": FilterOperatorFactory(),
            "Project": ProjectOperatorFactory(),
        }

    def build_operator(
        self,
        op_descriptor: str,
        child: ExecutionOperator | None = None,
    ) -> ExecutionOperator:
        prefix = op_descriptor.split("(")[0].strip()
        factory = self._factories.get(prefix)
        if not factory:
            raise UnknownOperatorError(f"No factory registered for operator prefix: {prefix}")
        return factory.create_operator(op_descriptor, self.data_sources, child)

    def build_pipeline(self, physical_descriptors: list[str]) -> ExecutionOperator | None:
        """Construct a chained execution operator pipeline from a list of physical descriptors (bottom-up)."""
        current_op: ExecutionOperator | None = None
        for desc in physical_descriptors:
            current_op = self.build_operator(desc, child=current_op)
        return current_op
