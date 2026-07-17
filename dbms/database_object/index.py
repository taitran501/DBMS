class Index:
    def __init__(self, index_id: str = "", name: str = "", index_type: str = "", unique: bool = False) -> None:
        self.index_id = index_id
        self.name = name
        self.type = index_type
        self.unique = unique

    def search(self, key: object) -> list:
        return []

    def insert_key(self, key: object, row_id: str) -> bool:
        return True

    def delete_key(self, key: object) -> bool:
        return True
