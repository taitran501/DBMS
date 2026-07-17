class Row:
    def __init__(self, row_id: str, values: list | dict, version: str) -> None:
        self.row_id = row_id
        self.values = values
        self.version = version

    def read(self) -> list | dict:
        return self.values

    def update(self, new_values: list | dict) -> bool:
        self.values = new_values
        return True
