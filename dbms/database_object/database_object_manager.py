from dbms.database_object.metadata_manager import MetadataManager


class DatabaseObjectManager:
    def __init__(self, metadata_manager: MetadataManager) -> None:
        self.metadata_manager = metadata_manager

    def get_object(self, name: str) -> object | None:
        return None

    def object_exists(self, name: str) -> bool:
        return True
