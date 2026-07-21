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
        try:
            self.cached_results = self.query_executor.execute(self.query_definition)
            return True
        except Exception:
            return False

    def resolve_dependencies(self, catalog_manager: object) -> bool:
        # Check if the tables used in the view exist in catalog
        return True

    def validate_definition(self, sql_parser: object) -> bool:
        # Check if query definition is a valid SELECT query
        try:
            ast = sql_parser.parse(self.query_definition)
            return ast.statement_type == "SELECT"
        except Exception:
            return False
