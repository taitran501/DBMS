class StoragePathError(Exception):
    pass


class BufferPoolFullError(Exception):
    pass


class RecordNotFoundError(Exception):
    pass


class StorageExhaustedError(Exception):
    pass


class StorageEngineNotInitializedError(Exception):
    pass
