from dbms.query_processing.query_executor import QueryExecutor
from dbms.query_processing.query_validator import QueryValidator
from dbms.query_processing.sql_parser import SQLParser


class QueryProcessor:
    def __init__(
        self,
        sql_parser: SQLParser,
        query_validator: QueryValidator,
        query_executor: QueryExecutor,
    ) -> None:
        self.sql_parser = sql_parser
        self.query_validator = query_validator
        self.query_executor = query_executor

    def process(self, sql: str, session: object | None = None) -> object | None:
        return None
