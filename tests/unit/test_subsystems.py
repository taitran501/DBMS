import pytest
from dbms.database import Database
from dbms.database_object.schema_management.schema import TableSchema, ColumnSchema
from dbms.database_object.column_management.column_manager import Column
from dbms.database_object.relationship_management.relationship_manager import Relationship

# Mocks to verify DIP (Dependency Inversion Principle)
class MockCatalog:
    def __init__(self):
        self.called_create = False
    def create_table(self, schema):
        self.called_create = True

class MockIndexManager:
    def __init__(self):
        self.called_create_index = False
    def create_index(self, index_name, table_name, column_name):
        self.called_create_index = True

def test_inject_database_object_dependencies_delegates_calls_to_custom_managers():
    # Injecting mock instances
    mock_catalog = MockCatalog()
    mock_index_mgr = MockIndexManager()
    
    from dbms.subsystems import DatabaseObjectManager
    custom_manager = DatabaseObjectManager(catalog=mock_catalog, index_manager=mock_index_mgr)
    
    db = Database(database_object_manager=custom_manager)
    
    # Test method delegating to the injected mock catalog
    schema = TableSchema("users", [])
    db.create_table(schema)
    assert mock_catalog.called_create is True
    
    # Test method delegating to the injected mock index manager
    db.create_index("idx_name", "users", "id")
    assert mock_index_mgr.called_create_index is True

def test_database_exposes_database_object_subsystem():
    db = Database()

    assert db.database_object.catalog is db.catalog
    assert db.database_object.index_manager is db.index_manager
    assert db.database_object.database_manager is not None
    assert db.database_object.schema_manager is not None
    assert db.database_object.table_manager is not None
    assert db.database_object.column_manager is not None
    assert db.database_object.data_type_manager is not None
    assert db.database_object.relationship_manager is not None

def test_create_table_registers_schema_in_database_catalog():
    db = Database()
    schema = TableSchema(
        name="users",
        columns=[
            ColumnSchema("id", "INT"),
            ColumnSchema("name", "TEXT"),
        ],
    )
    db.create_table(schema)
    assert db.catalog.has_table("users") is True
    assert db.catalog.get_table("users").column_names() == ["id", "name"]

def test_create_get_and_drop_database_updates_registry_and_rejects_missing_lookup():
    db = Database()
    mgr = db.database_object.database_manager
    
    db_obj = mgr.create_database("test_db")
    assert db_obj.name == "test_db"
    assert mgr.get_database("test_db") is db_obj
    
    mgr.drop_database("test_db")
    with pytest.raises(ValueError):
        mgr.get_database("test_db")

def test_create_get_and_drop_schema_updates_catalog_and_rejects_missing_lookup():
    db = Database()
    mgr = db.database_object.schema_manager
    
    schema_obj = mgr.create_schema("db1", "public")
    assert schema_obj.name == "public"
    assert mgr.get_schema("db1", "public") is schema_obj
    
    mgr.drop_schema("db1", "public")
    with pytest.raises(ValueError):
        mgr.get_schema("db1", "public")

def test_create_get_and_drop_table_updates_manager_and_rejects_missing_lookup():
    db = Database()
    mgr = db.database_object.table_manager
    schema = TableSchema("users", [])
    
    table_obj = mgr.create_table("public", "users", schema)
    assert table_obj.name == "users"
    assert mgr.get_table("public", "users") is table_obj
    
    mgr.drop_table("public", "users")
    with pytest.raises(ValueError):
        mgr.get_table("public", "users")

def test_add_get_and_drop_column_updates_manager_and_rejects_missing_lookup():
    db = Database()
    mgr = db.database_object.column_manager
    col = Column("id", "INT", nullable=False)
    
    mgr.add_column("users", col)
    assert mgr.get_column("users", "id") is col
    
    mgr.drop_column("users", "id")
    with pytest.raises(ValueError):
        mgr.get_column("users", "id")

def test_validate_value_accepts_matching_type_and_rejects_mismatched_type():
    db = Database()
    mgr = db.database_object.data_type_manager
    
    int_type = mgr.types["INT"]
    assert mgr.validate_value(int_type, 42) is True
    assert mgr.validate_value(int_type, "hello") is False

def test_create_and_drop_relationship_updates_relationship_registry():
    db = Database()
    mgr = db.database_object.relationship_manager
    rel = Relationship("fk_users_roles", "users", "roles", "MANY_TO_ONE")
    
    mgr.create_relationship(rel)
    assert mgr.relationships["fk_users_roles"] is rel
    
    mgr.drop_relationship("fk_users_roles")
    assert "fk_users_roles" not in mgr.relationships

def test_custom_descriptors_preserve_configuration_and_reject_invalid_page_size():
    # 1. Test DatabaseConfiguration & DatabaseDescriptor
    from dbms.database_object.database_management import DatabaseConfiguration, DatabaseDescriptor
    
    config = DatabaseConfiguration(page_size=8192, encoding="utf-16", max_size_mb=2048)
    descriptor = DatabaseDescriptor("finance_db", config)
    
    assert descriptor.name == "finance_db"
    assert descriptor.config.page_size == 8192
    assert descriptor.config.encoding == "utf-16"
    assert descriptor.config.max_size_mb == 2048

    # Test DatabaseManager validation with custom config
    db = Database()
    db_mgr = db.database_object.database_manager
    custom_db = db_mgr.create_database("my_custom_db", config)
    assert custom_db.descriptor.config.page_size == 8192
    
    # Test invalid config size raises ValueError
    invalid_config = DatabaseConfiguration(page_size=0)
    with pytest.raises(ValueError, match="Page size must be positive"):
        db_mgr.create_database("invalid_db", invalid_config)

    # 2. Test SchemaDescriptor
    schema_mgr = db.database_object.schema_manager
    custom_schema = schema_mgr.create_schema("my_custom_db", "auth_schema", version="2.0.1")
    assert custom_schema.descriptor.name == "auth_schema"
    assert custom_schema.descriptor.version == "2.0.1"

    # 3. Test ColumnDescriptor and TableDescriptor
    from dbms.database_object.column_management import ColumnDescriptor
    
    col_desc = ColumnDescriptor("email", "VARCHAR(255)", nullable=False, default_value="N/A")
    assert col_desc.name == "email"
    assert col_desc.data_type == "VARCHAR(255)"
    assert col_desc.nullable is False
    assert col_desc.default_value == "N/A"
    
    col_obj = Column(col_desc)
    assert col_obj.name == "email"
    assert col_obj.nullable is False
    
    # Test TableDescriptor metadata
    table_schema = TableSchema("members", [ColumnSchema("id", "INT")])
    table_mgr = db.database_object.table_manager
    table_obj = table_mgr.create_table("auth_schema", "members", table_schema, organization="INDEX_ORGANIZED", scope="TEMPORARY")
    
    assert table_obj.descriptor.name == "members"
    assert table_obj.descriptor.organization == "INDEX_ORGANIZED"
    assert table_obj.descriptor.scope == "TEMPORARY"
    assert len(table_obj.descriptor.columns) == 1
    assert table_obj.descriptor.columns[0].name == "id"

def test_view_dependency_graph_records_dependency():
    from dbms.database_object.view_management import ViewDependencyGraph

    graph = ViewDependencyGraph()
    graph.add_view_dependency("active_users", "users")

    assert graph.dependencies["active_users"] == ["users"]


def test_constraint_and_type_contracts_validate_values():
    from dbms.database_object.constraint_management import ConstraintDescriptor, ConstraintEnforcer
    from dbms.database_object.data_type_management import TypeConverter, TypeValidator

    constraint = ConstraintDescriptor("pk_users", "PRIMARY_KEY", ["id"])

    assert ConstraintEnforcer().validate_constraint(constraint, {"id": 1}) is True
    assert TypeValidator().validate_type_value("INT", 100) is True
    assert TypeConverter().convert_type_value("INT", "100") == 100


def test_index_maintainer_registers_and_removes_row():
    from dbms.database_object.index_management import IndexDescriptor, IndexMaintainer

    index = IndexDescriptor("idx_users_email", "B_TREE", ["email"], unique=True)
    maintainer = IndexMaintainer()
    maintainer.maintain_index_entry(index, "test@test.com", 1, "INSERT")

    assert maintainer.find_row_ids_by_key("test@test.com") == (1,)

    maintainer.maintain_index_entry(index, "test@test.com", 1, "DELETE")
    assert maintainer.find_row_ids_by_key("test@test.com") == ()


def test_procedure_and_trigger_executors_run_callable_bodies():
    from dbms.database_object.stored_procedure import ProcedureDescriptor, ProcedureExecutor
    from dbms.database_object.trigger_management import TriggerDescriptor, TriggerExecutor

    procedure = ProcedureDescriptor("add", ["a", "b"], lambda a, b: a + b)
    events = []
    trigger = TriggerDescriptor("audit", "INSERT", "AFTER", lambda context: events.append(context))

    assert ProcedureExecutor().execute_procedure_body(procedure, [2, 3]) == 5
    TriggerExecutor().execute_trigger_action(trigger, {"id": 1})
    assert events == [{"id": 1}]


def test_metadata_components_store_dependencies_and_statistics():
    from dbms.database_object.metadata_management import DependencyManager, MetadataManager, StatisticsManager

    metadata = MetadataManager()
    descriptor = object()
    metadata.register_metadata("table", "users", descriptor)
    dependencies = DependencyManager()
    dependencies.add_metadata_dependency("view:active_users", "table:users")
    statistics = StatisticsManager()
    statistics.update_statistics("users", "row_count", 500)

    assert metadata.get_metadata("table", "users") is descriptor
    assert dependencies.get_metadata_dependents("table:users") == ("view:active_users",)
    assert statistics.get_statistics("users", "row_count") == 500
