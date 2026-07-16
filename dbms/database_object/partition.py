class Partition:
    def __init__(self, partition_id: str, name: str, range: object) -> None:
        self.partition_id = partition_id
        self.name = name
        self.range = range

    def allocate_space(self) -> bool:
        return True

    def release_space(self) -> bool:
        return True
