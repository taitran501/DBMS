from dbms.database_object.dependencies import StorageAllocatorProtocol


class Partition:
    def __init__(
        self,
        partition_id: str,
        name: str,
        range: object,
        storage_allocator: StorageAllocatorProtocol,
    ) -> None:
        self.partition_id = partition_id
        self.name = name
        self.range = range
        self.storage_allocator = storage_allocator

    def allocate_space(self) -> bool:
        return True

    def release_space(self) -> bool:
        return True
