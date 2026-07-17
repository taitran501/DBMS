from dbms.database_object.constraint import Constraint


class ForeignKey(Constraint):
    def __init__(self, reference_table: object = None, on_delete: str = "restrict", on_update: str = "restrict") -> None:
        super().__init__(constraint_type="foreign_key")
        self.reference_table = reference_table
        self.on_delete = on_delete
        self.on_update = on_update

    def validate_reference(self) -> bool:
        return True
