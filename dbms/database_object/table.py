class Table:
    def __init__(self, table_id: str = "", name: str = "", columns: list | None = None, row_count: int = 0) -> None:
        self.table_id = table_id
        self.name = name
        self.columns = [] if columns is None else columns
        self.row_count = row_count

    def insert(self, row: object) -> bool:
        return True

    def update(self, row_id: str, new_values: dict) -> bool:
        return True

    def delete(self, row_id: str) -> bool:
        return True

    def truncate(self) -> bool:
        return True
