from __future__ import annotations

from dbms.database_object.stored_procedure import StoredProcedure
from dbms.database_object.table import Table
from dbms.database_object.view import View


class Schema:
    """Composite component managing tables, views, and stored procedures within a schema."""

    def __init__(
        self,
        schema_id: str = "",
        name: str = "",
        owner: str = "",
        tables: dict[str, Table] | None = None,
        views: dict[str, View] | None = None,
        stored_procedures: dict[str, StoredProcedure] | None = None,
    ) -> None:
        self.schema_id = schema_id
        self.name = name
        self.owner = owner
        self.tables = {} if tables is None else tables
        self.views = {} if views is None else views
        self.stored_procedures = {} if stored_procedures is None else stored_procedures

    # Table operations
    def create_table(self, table: Table) -> bool:
        if table.name in self.tables:
            raise ValueError(f"Table '{table.name}' already exists in schema '{self.name}'")
        self.tables[table.name] = table
        return True

    def get_table(self, name: str) -> Table:
        if name not in self.tables:
            raise KeyError(f"Table '{name}' not found in schema '{self.name}'")
        return self.tables[name]

    def rename_table(self, old_name: str, new_name: str) -> bool:
        if old_name not in self.tables:
            raise KeyError(f"Table '{old_name}' not found in schema '{self.name}'")
        if new_name in self.tables:
            raise ValueError(f"Table '{new_name}' already exists in schema '{self.name}'")
        table = self.tables.pop(old_name)
        table.name = new_name
        self.tables[new_name] = table
        return True

    def drop_table(self, name: str) -> bool:
        if name not in self.tables:
            raise KeyError(f"Table '{name}' not found in schema '{self.name}'")
        del self.tables[name]
        return True

    # View operations
    def create_view(self, view: View) -> bool:
        if view.name in self.views:
            raise ValueError(f"View '{view.name}' already exists in schema '{self.name}'")
        self.views[view.name] = view
        return True

    def get_view(self, name: str) -> View:
        if name not in self.views:
            raise KeyError(f"View '{name}' not found in schema '{self.name}'")
        return self.views[name]

    def drop_view(self, name: str) -> bool:
        if name not in self.views:
            raise KeyError(f"View '{name}' not found in schema '{self.name}'")
        del self.views[name]
        return True

    # StoredProcedure operations
    def create_stored_procedure(self, procedure: StoredProcedure) -> bool:
        if procedure.name in self.stored_procedures:
            raise ValueError(f"Stored procedure '{procedure.name}' already exists in schema '{self.name}'")
        self.stored_procedures[procedure.name] = procedure
        return True

    def get_stored_procedure(self, name: str) -> StoredProcedure:
        if name not in self.stored_procedures:
            raise KeyError(f"Stored procedure '{name}' not found in schema '{self.name}'")
        return self.stored_procedures[name]

    def drop_stored_procedure(self, name: str) -> bool:
        if name not in self.stored_procedures:
            raise KeyError(f"Stored procedure '{name}' not found in schema '{self.name}'")
        del self.stored_procedures[name]
        return True
