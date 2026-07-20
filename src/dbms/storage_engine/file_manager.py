class FileManager:
    def __init__(self, root_path: str = "") -> None:
        self.root_path = root_path

    def create_file(self, path: str) -> bool:
        return True

    def read(self, file: object) -> bytes:
        return b""

    def write(self, file: object, data: bytes) -> bool:
        return True
