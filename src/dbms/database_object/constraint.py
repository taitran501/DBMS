from dbms.database_object.row import Row


class Constraint:
    def __init__(self, constraint_id: str, name: str, constraint_type: str, validation_rule: object) -> None:
        self.constraint_id = constraint_id
        self.name = name
        self.constraint_type = constraint_type
        self.validation_rule = validation_rule

    def validate_row(self, row: Row) -> bool:
        return True
