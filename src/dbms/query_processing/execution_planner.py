from typing import Any

from dbms.query_processing.ast import AST, CreateTableNode, InsertNode, SelectNode
from dbms.query_processing.execution_operator import (
    CreateTableOperator,
    ExecutionOperator,
    InsertOperator,
    MutationOperator,
)
from dbms.query_processing.execution_plan_factory import ExecutionPlanFactory
from dbms.query_processing.logical_plan import LogicalPlan
from dbms.query_processing.query_optimizer import QueryOptimizer


class ExecutionPlanner:
    """Optimizes AST statements into executable query or mutation pipelines."""

    def __init__(
        self,
        data_sources: dict[str, list[dict[str, Any]]] | None = None,
        schema_catalog: dict[str, list[str]] | None = None,
        available_indexes: dict[str, str] | None = None,
        table_cardinalities: dict[str, int] | None = None,
        query_optimizer: QueryOptimizer | None = None,
    ) -> None:
        self.data_sources = {} if data_sources is None else data_sources
        self.schema_catalog = {} if schema_catalog is None else schema_catalog
        self.available_indexes = {} if available_indexes is None else available_indexes
        self.table_cardinalities = (
            {} if table_cardinalities is None else table_cardinalities
        )
        self.query_optimizer = query_optimizer or QueryOptimizer()
        self.execution_plan_factory = ExecutionPlanFactory(self.data_sources)

    def configure_context(
        self,
        data_sources: dict[str, list[dict[str, Any]]],
        schema_catalog: dict[str, list[str]] | None = None,
        available_indexes: dict[str, str] | None = None,
        table_cardinalities: dict[str, int] | None = None,
    ) -> None:
        """Refresh the mutable request-scoped data and planning metadata."""
        self.data_sources = data_sources
        self.schema_catalog = {} if schema_catalog is None else schema_catalog
        self.available_indexes = {} if available_indexes is None else available_indexes
        self.table_cardinalities = (
            {} if table_cardinalities is None else table_cardinalities
        )
        self.execution_plan_factory.data_sources = data_sources

    def _build_select_logical_plan(self, node: SelectNode) -> LogicalPlan:
        operators = [f"TableScan({node.table_name})"]
        if node.where_clause is not None:
            operators.append(f"Filter({self._format_predicate(node.where_clause)})")
        if node.columns and node.columns != ["*"]:
            operators.append(f"Project({', '.join(node.columns)})")

        plan = LogicalPlan(operators)
        plan.available_indexes = self.available_indexes
        plan.table_cardinalities = self.table_cardinalities
        plan.output_columns = node.columns
        plan.estimated_cost = float(
            self.table_cardinalities.get(
                node.table_name, len(self.data_sources.get(node.table_name, []))
            )
        )
        return plan

    @staticmethod
    def _format_predicate(predicate: object) -> str:
        if hasattr(predicate, "left") and hasattr(predicate, "operator") and hasattr(predicate, "right"):
            left = getattr(predicate.left, "name", getattr(predicate.left, "value", predicate.left))
            right_value = getattr(predicate.right, "value", predicate.right)
            if isinstance(right_value, str):
                right_value = repr(right_value)
            return f"{left} {predicate.operator} {right_value}"
        if hasattr(predicate, "value"):
            return str(predicate.value)
        raise ValueError("Unsupported WHERE predicate for execution planning")

    def build(self, ast: AST) -> ExecutionOperator | MutationOperator:
        root = ast.root_node
        if isinstance(root, SelectNode):
            physical_plan = self.query_optimizer.optimize(
                self._build_select_logical_plan(root)
            )
            pipeline = self.execution_plan_factory.build_pipeline(
                physical_plan.operators
            )
            if pipeline is None:
                raise ValueError("SELECT planning produced an empty execution pipeline")
            return pipeline
        if isinstance(root, InsertNode):
            return InsertOperator(
                self.data_sources,
                self.schema_catalog,
                root.table_name,
                root.values,
            )
        if isinstance(root, CreateTableNode):
            return CreateTableOperator(
                self.data_sources,
                self.schema_catalog,
                root.table_name,
                root.columns,
            )
        raise NotImplementedError(
            f"Execution planning does not support {type(root).__name__}"
        )
