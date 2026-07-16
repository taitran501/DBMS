from dbms.query_processing.statement import Statement


class QueryExecutor:
    def execute(
        self,
        statement: Statement,
        transaction: object | None = None,
    ) -> object | None:
        return None
