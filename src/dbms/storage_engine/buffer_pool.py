from dbms.storage_engine.page import Page


class BufferPool:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity

    def pin_page(self, page_id: int) -> Page | None:
        return None

    def cache_page(self, page: Page) -> bool:
        return False

    def flush_page(self, page_id: int) -> bool:
        return False

    def flush_all_pages(self) -> bool:
        return False
