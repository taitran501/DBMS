from dbms.storage_engine.buffer_pool import BufferPool


class StorageEngine:
    def __init__(self, buffer_pool: BufferPool) -> None:
        self.buffer_pool = buffer_pool

    def read(self, page_id: int) -> object | None:
        return None

    def write(self, value: object) -> bool:
        return True

    def delete(self, record_id: int) -> bool:
        return True

    def revert(self, transaction_id: int) -> bool:
        return True
