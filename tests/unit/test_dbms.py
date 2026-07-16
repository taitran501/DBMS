from dbms.administration_operations.administration_operations_manager import (
    AdministrationOperationsManager,
)
from dbms.database_object.database_object_manager import DatabaseObjectManager
from dbms.database_object.metadata_manager import MetadataManager
from dbms.database_object.system_catalog import SystemCatalog
from dbms.dbms import DBMS
from dbms.durability.durability_manager import DurabilityManager
from dbms.durability.recovery_manager import RecoveryManager
from dbms.durability.transaction_log_manager import TransactionLogManager
from dbms.performance.performance_manager import PerformanceManager
from dbms.query_processing.query_executor import QueryExecutor
from dbms.query_processing.query_processor import QueryProcessor
from dbms.query_processing.query_validator import QueryValidator
from dbms.query_processing.sql_parser import SqlParser
from dbms.security_access_control.security_access_controller import (
    SecurityAccessController,
)
from dbms.storage_engine.storage_engine import StorageEngine
from dbms.storage_engine.buffer_pool import BufferPool
from dbms.transaction.transaction_manager import TransactionManager


def create_dbms():
    metadata_manager = MetadataManager(SystemCatalog())
    transaction_log_manager = TransactionLogManager()
    recovery_manager = RecoveryManager(transaction_log_manager)
    dependencies = {
        "database_object_manager": DatabaseObjectManager(metadata_manager),
        "transaction_manager": TransactionManager(),
        "storage_engine": StorageEngine(BufferPool(16)),
        "durability_manager": DurabilityManager(
            transaction_log_manager,
            recovery_manager,
        ),
        "query_processor": QueryProcessor(
            SqlParser(),
            QueryValidator(),
            QueryExecutor(),
        ),
        "security_access_controller": SecurityAccessController(),
        "performance_manager": PerformanceManager(),
        "administration_operations_manager": AdministrationOperationsManager(),
    }
    return DBMS(**dependencies), dependencies


def test_dbms_stores_its_eight_module_dependencies():
    dbms, dependencies = create_dbms()

    for attribute_name, dependency in dependencies.items():
        assert getattr(dbms, attribute_name) is dependency


def test_dbms_lifecycle_methods_return_placeholder_success():
    dbms, _ = create_dbms()

    assert dbms.start() is True
    assert dbms.shutdown() is True


def test_dbms_execute_returns_placeholder_result():
    dbms, _ = create_dbms()

    assert dbms.execute("SELECT 1") is None
