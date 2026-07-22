from dbms.database_object.constraint import Constraint
from dbms.database_object.table import Table


class ForeignKey(Constraint):
    def __init__(
        self,
        constraint_id: str,
        reference_table: Table,
        reference_column: str,
        on_delete: str,
        on_update: str,
    ) -> None:
        super().__init__(constraint_id, constraint_id, "foreign_key", None)
        self.reference_table = reference_table
        self.reference_column = reference_column
        self.on_delete = on_delete
        self.on_update = on_update

    def validate_reference(self, value: object) -> bool:
        if self.reference_table is not None and hasattr(self.reference_table, "check_key_exists"):
            return bool(self.reference_table.check_key_exists(value))
        return True
