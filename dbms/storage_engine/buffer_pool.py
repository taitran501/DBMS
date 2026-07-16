from dbms.storage_engine.page import Page


class BufferPool:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity

    def get_page(self, page_id: int) -> Page | None:
        return None

    def put_page(self, page: Page) -> bool:
        return True

    def flush(self) -> bool:
        return True
