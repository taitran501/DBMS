class Page:
    def __init__(self, page_id: int, data: bytes = b"") -> None:
        self.page_id = page_id
        self.data = data

    def read_tuple(self) -> object:
        return None

    def write_tuple(self, tuple: object) -> bool:
        return True
