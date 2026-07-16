from dbms.administration_operations.administration_operations_manager import (
    AdministrationOperationsManager,
)
from dbms.database_object.database_object_manager import DatabaseObjectManager
from dbms.durability.durability_manager import DurabilityManager
from dbms.performance.performance_manager import PerformanceManager
from dbms.query_processing.query_processor import QueryProcessor
from dbms.security_access_control.security_access_controller import (
    SecurityAccessController,
)
from dbms.storage_engine.storage_engine import StorageEngine
from dbms.transaction.transaction_manager import TransactionManager


class DBMS:
"""Quản lý tám module chính của hệ quản trị cơ sở dữ liệu."""
    def __init__(
        self,
        database_object_manager: DatabaseObjectManager,
        transaction_manager: TransactionManager,
        storage_engine: StorageEngine,
        durability_manager: DurabilityManager,
        query_processor: QueryProcessor,
        security_access_controller: SecurityAccessController,
        performance_manager: PerformanceManager,
        administration_operations_manager: AdministrationOperationsManager,
    ) -> None:
        self.database_object_manager = database_object_manager
        self.transaction_manager = transaction_manager
        self.storage_engine = storage_engine
        self.durability_manager = durability_manager
        self.query_processor = query_processor
        self.security_access_controller = security_access_controller
        self.performance_manager = performance_manager
        self.administration_operations_manager = administration_operations_manager

    def start(self) -> bool:
        return True

    def shutdown(self) -> bool:
        return True

    def execute(self, sql: str, session: object | None = None) -> object | None:
        return None
