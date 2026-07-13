from dbms.database_object.metadata_management.system_catalog import Catalog
from dbms.database_object.index_management.index_manager import IndexManager
from dbms.subsystems import DatabaseObjectManager

class Database:
    def __init__(self, database_object_manager: DatabaseObjectManager = None):
        if database_object_manager is None:
            database_object_manager = DatabaseObjectManager(Catalog(), IndexManager())
        self.database_object = database_object_manager
        
        # Backward-compatible attributes
        self.catalog = self.database_object.catalog
        self.index_manager = self.database_object.index_manager

    def create_table(self, schema) -> None:
        self.database_object.create_table(schema)

    def create_index(self, index_name: str, table_name: str, column_name: str) -> None:
        self.database_object.create_index(index_name, table_name, column_name)
