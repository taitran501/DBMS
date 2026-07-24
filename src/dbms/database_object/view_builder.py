from dbms.database_object.dependencies import QueryExecutorProtocol
from dbms.database_object.view import View


class ViewBuilder:
    def __init__(self, name: str = "", query_definition: str = "") -> None:
        self._name = name
        self._query_definition = query_definition
        self._view_id: str | None = None
        self._query_executor: QueryExecutorProtocol | None = None
        self._cached_results: object | None = None

    def set_view_id(self, view_id: str) -> "ViewBuilder":
        self._view_id = view_id
        return self

    def set_name(self, name: str) -> "ViewBuilder":
        self._name = name
        return self

    def set_query_definition(self, query_definition: str) -> "ViewBuilder":
        self._query_definition = query_definition
        return self

    def set_query_executor(
        self, query_executor: QueryExecutorProtocol
    ) -> "ViewBuilder":
        self._query_executor = query_executor
        return self

    def set_cached_results(self, cached_results: object) -> "ViewBuilder":
        self._cached_results = cached_results
        return self

    def build(self) -> View:
        if not self._name or not isinstance(self._name, str) or not self._name.strip():
            raise ValueError("View name cannot be empty")
        if (
            not self._query_definition
            or not isinstance(self._query_definition, str)
            or not self._query_definition.strip()
        ):
            raise ValueError("Query definition cannot be empty")

        view_id = self._view_id if self._view_id is not None else f"view_{self._name}"
        return View(
            view_id=view_id,
            name=self._name,
            query_definition=self._query_definition,
            query_executor=self._query_executor,
            cached_results=self._cached_results,
        )
