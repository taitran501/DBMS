class Constraint:
    def __init__(self, constraint_id: str = "", name: str = "", constraint_type: str = "") -> None:
        self.constraint_id = constraint_id
        self.name = name
        self.constraint_type = constraint_type

    def validate_row(self, row: object) -> bool:
        return True
