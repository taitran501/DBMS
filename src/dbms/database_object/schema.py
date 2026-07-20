from dbms.database_object.table import Table


class Schema:
    def __init__(
        self,
        schema_id: str = "",
        name: str = "",
        owner: str = "",
        tables: dict[str, Table] | None = None,
    ) -> None:
        self.schema_id = schema_id
        self.name = name
        self.owner = owner
        self.tables = {} if tables is None else tables

    def create_table(self, name: str) -> Table:
        return None

    def drop_table(self, name: str) -> bool:
        return True
