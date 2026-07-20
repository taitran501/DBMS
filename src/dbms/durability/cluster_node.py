class ClusterNode:
    def __init__(self, node_id: str, address: str) -> None:
        self.node_id = node_id
        self.address = address

    def ping(self) -> bool:
        return True
