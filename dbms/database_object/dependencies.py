from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from dbms.database_object.database import Database


@runtime_checkable
class MetadataCacheProtocol(Protocol):
    def set(self, name: str, descriptor: object) -> None: ...

    def remove(self, name: str) -> None: ...

    def get(self, name: str) -> object | None: ...


@runtime_checkable
class DatabaseStorageProtocol(Protocol):
    def load_schema_metadata(self, database: object) -> object: ...

    def flush_dirty_pages(self, database: object) -> None: ...

    def delete_database_files(self, name: str) -> None: ...


@runtime_checkable
class DatabaseBackupProtocol(Protocol):
    def create_backup(self, database: object) -> object: ...

    def restore_backup(self, database: object) -> object: ...


@runtime_checkable
class StorageAllocatorProtocol(Protocol):
    def allocate_space(self, partition: object) -> object: ...

    def release_space(self, partition: object) -> None: ...


@runtime_checkable
class QueryExecutorProtocol(Protocol):
    def execute(self, query_or_plan: object) -> object: ...


@runtime_checkable
class DatabaseFactoryProtocol(Protocol):
    def create(self, name: str) -> Database: ...
