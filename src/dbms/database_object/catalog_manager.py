from dbms.database_object.dependencies import MetadataCacheProtocol


class CatalogManager:
    """Repository facade for catalog metadata stored in an injected cache."""

    def __init__(self, metadata_cache: MetadataCacheProtocol) -> None:
        self.metadata_cache = metadata_cache

    def register_object(self, name: str, descriptor: object) -> bool:
        self.metadata_cache.set(name, descriptor)
        return True

    def remove_object(self, name: str) -> bool:
        self.metadata_cache.remove(name)
        return True

    def lookup_object(self, name: str) -> object:
        descriptor = self.metadata_cache.get(name)
        if descriptor is None:
            raise KeyError(f"Metadata object '{name}' not found")
        return descriptor
