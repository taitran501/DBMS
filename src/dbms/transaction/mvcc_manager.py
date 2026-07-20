class MVCCManager:
    def __init__(self, version_chain_map: dict) -> None:
        self.version_chain_map = version_chain_map

    def create_snapshot(self) -> object:
        return None

    def read_visible_version(self, row: object, tx: object) -> object:
        return row
