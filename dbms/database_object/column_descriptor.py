class ColumnDescriptor:
    def __init__(self, name: str, data_type: str, nullable: bool = True) -> None:
        self.name = name
        self.data_type = data_type
        self.nullable = nullable
