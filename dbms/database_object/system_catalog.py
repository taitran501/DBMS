class SystemCatalog:
    def register(self, name: str, descriptor: object) -> bool:
        return True

    def find(self, name: str) -> object | None:
        return None

    def remove(self, name: str) -> bool:
        return True
