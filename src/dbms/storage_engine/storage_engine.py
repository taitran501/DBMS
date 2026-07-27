from dbms.storage_engine.buffer_pool import BufferPool
from dbms.storage_engine.exceptions import StorageEngineNotInitializedError


class StorageEngine:
    """Facade for the Storage Engine managing initialization and page I/O via BufferPool."""

    def __init__(self, buffer_pool: BufferPool) -> None:
        self.buffer_pool: BufferPool = buffer_pool
        self.is_initialized: bool = False

    def initialize(self) -> bool:
        self.is_initialized = True
        return True

    def read_page(self, page_id: int) -> object | None:
        if not self.is_initialized:
            raise StorageEngineNotInitializedError("StorageEngine is not initialized.")
        return self.buffer_pool.pin_page(page_id)

    def write_page(self, page: object) -> bool:
        if not self.is_initialized:
            raise StorageEngineNotInitializedError("StorageEngine is not initialized.")
        return self.buffer_pool.cache_page(page)
