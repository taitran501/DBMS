class Row:
    def __init__(self, row_id: str, values: list, version: str) -> None:
        self.row_id = row_id
        self.values = values
        self.version = version

    def read(self) -> list:
        return self.values

    def update(self, new_values: list) -> bool:
        self.values = new_values
        return True
