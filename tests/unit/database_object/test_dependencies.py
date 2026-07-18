from dbms.database_object.dependencies import (
    DatabaseBackupProtocol,
    DatabaseFactoryProtocol,
    DatabaseStorageProtocol,
    MetadataCacheProtocol,
    QueryExecutorProtocol,
    StorageAllocatorProtocol,
)
from dbms.database_object.database import Database


def test_metadata_cache_stub_matches_protocol():
    # Arrange
    class MetadataCacheStub:
        def set(self, name: str, descriptor: object) -> None: ...
        def remove(self, name: str) -> None: ...
        def get(self, name: str) -> object | None: ...

    # Assert
    assert isinstance(MetadataCacheStub(), MetadataCacheProtocol)


def test_database_storage_stub_matches_protocol():
    # Arrange
    class DatabaseStorageStub:
        def load_schema_metadata(self, database: object) -> object: ...
        def flush_dirty_pages(self, database: object) -> None: ...
        def delete_database_files(self, name: str) -> None: ...

    # Assert
    assert isinstance(DatabaseStorageStub(), DatabaseStorageProtocol)


def test_database_backup_stub_matches_protocol():
    # Arrange
    class DatabaseBackupStub:
        def create_backup(self, database: object) -> object: ...
        def restore_backup(self, database: object) -> object: ...

    # Assert
    assert isinstance(DatabaseBackupStub(), DatabaseBackupProtocol)


def test_storage_allocator_stub_matches_protocol():
    # Arrange
    class StorageAllocatorStub:
        def allocate_space(self, partition: object) -> object: ...
        def release_space(self, partition: object) -> None: ...

    # Assert
    assert isinstance(StorageAllocatorStub(), StorageAllocatorProtocol)


def test_query_executor_stub_matches_protocol():
    # Arrange
    class QueryExecutorStub:
        def execute(self, query_or_plan: object) -> object: ...

    # Assert
    assert isinstance(QueryExecutorStub(), QueryExecutorProtocol)


def test_database_factory_stub_matches_protocol():
    # Arrange
    class DatabaseFactoryStub:
        def create(self, name: str) -> Database: ...

    # Assert
    assert isinstance(DatabaseFactoryStub(), DatabaseFactoryProtocol)
