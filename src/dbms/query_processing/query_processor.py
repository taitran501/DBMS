from typing import Any

from dbms.query_processing.execution_planner import ExecutionPlanner
from dbms.query_processing.query_executor import QueryExecutor
from dbms.query_processing.query_validator import QueryValidator
from dbms.query_processing.sql_parser import SQLParser


class QueryProcessor:
    def __init__(
        self,
        sql_parser: SQLParser,
        query_validator: QueryValidator,
        query_executor: QueryExecutor,
        execution_planner: ExecutionPlanner | None = None,
    ) -> None:
        self.sql_parser = sql_parser
        self.query_validator = query_validator
        self.query_executor = query_executor
        self.execution_planner = execution_planner or ExecutionPlanner()

    def process(self, sql: str, session: dict[str, Any] | None = None) -> object | None:
        """Parse, validate, plan, and execute a supported SQL statement."""
        context = {} if session is None else session
        ast = self.sql_parser.parse_sql(sql)

        if not self.query_validator.validate(ast, context):
            details = "; ".join(self.query_validator.errors)
            raise ValueError(f"Query validation failed: {details}")

        data_sources = context.get("data_sources")
        if data_sources is not None:
            self.execution_planner.data_sources = data_sources

        pipeline = self.execution_planner.build(ast)
        return self.query_executor.execute(pipeline, transaction=context.get("transaction"))
