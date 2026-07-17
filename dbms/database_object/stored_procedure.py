from dbms.database_object.dependencies import QueryExecutorProtocol


class StoredProcedure:
    def __init__(
        self,
        procedure_id: str,
        name: str,
        query_plan: object,
        query_executor: QueryExecutorProtocol,
    ) -> None:
        self.procedure_id = procedure_id
        self.name = name
        self.query_plan = query_plan
        self.query_executor = query_executor

    def execute(self) -> object:
        return None
