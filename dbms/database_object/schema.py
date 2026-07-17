class Schema:
    def __init__(self, schema_id: str = "", name: str = "", owner: str = "") -> None:
        self.schema_id = schema_id
        self.name = name
        self.owner = owner

    def create_table(self, name: str) -> object:
        return None

    def drop_table(self, name: str) -> bool:
        return True
