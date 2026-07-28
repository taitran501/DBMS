from typing import Any

from dbms.query_processing.ast import AST, SelectNode
from dbms.query_processing.ast_visitor import PhysicalPlanGeneratorVisitor
from dbms.query_processing.execution_operator import ExecutionOperator


class ExecutionPlanner:
    """Builds an executable iterator pipeline for the currently supported SELECT AST."""

    def __init__(self, data_sources: dict[str, list[dict[str, Any]]] | None = None) -> None:
        self.data_sources = {} if data_sources is None else data_sources

    def build(self, ast: AST) -> ExecutionOperator:
        if not isinstance(ast.root_node, SelectNode):
            raise NotImplementedError("Execution planning currently supports SELECT statements only")

        visitor = PhysicalPlanGeneratorVisitor(self.data_sources)
        return ast.accept(visitor)
