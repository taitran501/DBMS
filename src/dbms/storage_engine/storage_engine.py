from dbms.storage_engine.buffer_pool import BufferPool


class StorageEngine:
    def __init__(self, buffer_pool: BufferPool) -> None:
        self.buffer_pool = buffer_pool

    def initialize(self) -> bool:
        return False

    def read_page(self, page_id: int) -> object | None:
        return None

    def write_page(self, page: object) -> bool:
        return False
