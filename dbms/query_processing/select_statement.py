from dbms.query_processing.statement import Statement


class SelectStatement(Statement):
    def __init__(
        self,
        table_name: str,
        columns: list[str],
        where: object | None = None,
    ) -> None:
        super().__init__("SELECT")
        self.table_name = table_name
        self.columns = columns
        self.where = where
