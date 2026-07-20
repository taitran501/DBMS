from dbms.database_object.dependencies import QueryExecutorProtocol


class View:
    def __init__(
        self,
        view_id: str,
        name: str,
        query_definition: str,
        query_executor: QueryExecutorProtocol,
        cached_results: object,
    ) -> None:
        self.view_id = view_id
        self.name = name
        self.query_definition = query_definition
        self.query_executor = query_executor
        self.cached_results = cached_results

    def create_view(self) -> bool:
        return True

    def refresh(self) -> bool:
        return True
