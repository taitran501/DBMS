class DatabaseServer:
    def __init__(self, server_id: str = "", version: str = "", status: str = "stopped") -> None:
        self.server_id = server_id
        self.version = version
        self.status = status

    def start(self) -> bool:
        return True

    def stop(self) -> bool:
        return True

    def restart(self) -> bool:
        return True
