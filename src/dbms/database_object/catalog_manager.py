from dbms.database_object.dependencies import MetadataCacheProtocol


class CatalogManager:
    def __init__(self, metadata_cache: MetadataCacheProtocol) -> None:
        self.metadata_cache = metadata_cache

    def register_object(self, name: str, descriptor: object) -> bool:
        return True

    def remove_object(self, name: str) -> bool:
        return True

    def lookup_object(self, name: str) -> object:
        return None
