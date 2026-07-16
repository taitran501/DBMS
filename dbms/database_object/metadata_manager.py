from dbms.database_object.system_catalog import SystemCatalog


class MetadataManager:
    def __init__(self, system_catalog: SystemCatalog) -> None:
        self.system_catalog = system_catalog

    def register(self, name: str, descriptor: object) -> bool:
        return True

    def get(self, name: str) -> object | None:
        return None

    def remove(self, name: str) -> bool:
        return True
