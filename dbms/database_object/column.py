class Column:
    def __init__(self, column_id: str = "", name: str = "", data_type: object = None, nullable: bool = True) -> None:
        self.column_id = column_id
        self.name = name
        self.data_type = data_type
        self.nullable = nullable

    def validate(self, value: object) -> bool:
        return True
