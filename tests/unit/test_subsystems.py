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

def test_database_dependency_injection():
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

def test_database_object_manager_create_table():
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

def test_database_manager():
    db = Database()
    mgr = db.database_object.database_manager
    
    db_obj = mgr.create_database("test_db")
    assert db_obj.name == "test_db"
    assert mgr.get_database("test_db") is db_obj
    
    mgr.drop_database("test_db")
    with pytest.raises(ValueError):
        mgr.get_database("test_db")

def test_schema_manager():
    db = Database()
    mgr = db.database_object.schema_manager
    
    schema_obj = mgr.create_schema("db1", "public")
    assert schema_obj.name == "public"
    assert mgr.get_schema("db1", "public") is schema_obj
    
    mgr.drop_schema("db1", "public")
    with pytest.raises(ValueError):
        mgr.get_schema("db1", "public")

def test_table_manager():
    db = Database()
    mgr = db.database_object.table_manager
    schema = TableSchema("users", [])
    
    table_obj = mgr.create_table("public", "users", schema)
    assert table_obj.name == "users"
    assert mgr.get_table("public", "users") is table_obj
    
    mgr.drop_table("public", "users")
    with pytest.raises(ValueError):
        mgr.get_table("public", "users")

def test_column_manager():
    db = Database()
    mgr = db.database_object.column_manager
    col = Column("id", "INT", nullable=False)
    
    mgr.add_column("users", col)
    assert mgr.get_column("users", "id") is col
    
    mgr.drop_column("users", "id")
    with pytest.raises(ValueError):
        mgr.get_column("users", "id")

def test_data_type_manager():
    db = Database()
    mgr = db.database_object.data_type_manager
    
    int_type = mgr.types["INT"]
    assert mgr.validate_value(int_type, 42) is True
    assert mgr.validate_value(int_type, "hello") is False

def test_relationship_manager():
    db = Database()
    mgr = db.database_object.relationship_manager
    rel = Relationship("fk_users_roles", "users", "roles", "MANY_TO_ONE")
    
    mgr.create_relationship(rel)
    assert mgr.relationships["fk_users_roles"] is rel
    
    mgr.drop_relationship("fk_users_roles")
    assert "fk_users_roles" not in mgr.relationships

def test_descriptors_and_configurations():
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

def test_mindmap_classes_completeness():
    # 1. Database Registry
    from dbms.database_object.database_management import DatabaseRegistry
    registry = DatabaseRegistry()
    assert registry is not None

    # 2. Schema Catalog, Ownership Policy, Migration Ledger
    from dbms.database_object.schema_management import SchemaCatalog, SchemaOwnershipPolicy, SchemaMigrationLedger
    assert SchemaCatalog() is not None
    assert SchemaOwnershipPolicy() is not None
    assert SchemaMigrationLedger() is not None

    # 3. Table Organization, Scope
    from dbms.database_object.table_management import TableOrganization, TableScope
    assert TableOrganization.HEAP == "HEAP"
    assert TableScope.PERSISTENT == "PERSISTENT"

    # 4. View Descriptor & View Dependency Graph
    from dbms.database_object.view_management import ViewDescriptor, ViewDependencyGraph
    v_desc = ViewDescriptor("active_users", "SELECT * FROM users WHERE active = 1")
    assert v_desc.name == "active_users"
    v_graph = ViewDependencyGraph()
    v_graph.add_dependency("active_users", "users")
    assert "users" in v_graph.dependencies["active_users"]

    # 5. Relationship Descriptor & Referential Action Policy
    from dbms.database_object.relationship_management import RelationshipDescriptor, ReferentialActionPolicy
    r_desc = RelationshipDescriptor("fk_users_roles", "users", "roles", "MANY_TO_ONE")
    assert r_desc.source_table == "users"
    policy = ReferentialActionPolicy(on_delete="CASCADE")
    assert policy.on_delete == "CASCADE"

    # 6. Column RuleSet
    from dbms.database_object.column_management import ColumnRuleSet
    rules = ColumnRuleSet(is_primary_key=True)
    assert rules.is_primary_key is True

    # 7. Constraint Descriptor & Constraint Enforcer
    from dbms.database_object.constraint_management import ConstraintDescriptor, ConstraintEnforcer
    c_desc = ConstraintDescriptor("pk_users", "PRIMARY_KEY", ["id"])
    assert c_desc.columns == ["id"]
    enforcer = ConstraintEnforcer()
    assert enforcer.validate(c_desc, {"id": 1}) is True

    # 8. DataType Descriptor, Type Validator, Type Converter
    from dbms.database_object.data_type_management import DataTypeDescriptor, TypeValidator, TypeConverter
    dt_desc = DataTypeDescriptor("INT")
    assert dt_desc.name == "INT"
    validator = TypeValidator()
    assert validator.validate("INT", 100) is True
    converter = TypeConverter()
    assert converter.convert("INT", "100") == 100

    # 9. Index Descriptor, Index Access Method, Index Organization, Index Maintainer
    from dbms.database_object.index_management import IndexDescriptor, IndexAccessMethod, IndexOrganization, IndexMaintainer
    i_desc = IndexDescriptor("idx_users_email", "B_TREE", ["email"], unique=True)
    assert i_desc.unique is True
    assert IndexAccessMethod.B_TREE == "B_TREE"
    i_org = IndexOrganization()
    assert i_org.access_method == "B_TREE"
    maintainer = IndexMaintainer()
    maintainer.maintain(i_desc, "test@test.com", 1, "INSERT")

    # 10. Procedure Descriptor & Procedure Executor
    from dbms.database_object.stored_procedure import ProcedureDescriptor, ProcedureExecutor
    p_desc = ProcedureDescriptor("add_user", ["username", "email"], "INSERT INTO users ...")
    assert p_desc.parameters == ["username", "email"]
    executor = ProcedureExecutor()
    executor.execute(p_desc, ["alice", "alice@test.com"])

    # 11. Trigger Descriptor, Event Binding, Trigger Executor
    from dbms.database_object.trigger_management import TriggerDescriptor, TriggerEventBinding, TriggerExecutor
    tr_desc = TriggerDescriptor("tr_audit_users", "INSERT", "AFTER", "INSERT INTO audit_log ...")
    assert tr_desc.timing == "AFTER"
    binding = TriggerEventBinding("tr_audit_users", "INSERT")
    assert binding.event == "INSERT"
    tr_exec = TriggerExecutor()
    tr_exec.execute(tr_desc)

    # 12. Metadata Manager, System Catalog, Dependency Manager, Statistics Manager
    from dbms.database_object.metadata_management import SystemCatalog, DependencyManager, StatisticsManager, MetadataManager
    sys_catalog = SystemCatalog()
    assert sys_catalog is not None
    dep_mgr = DependencyManager()
    dep_mgr.register_dependency("view_users", "users")
    assert "view_users" in dep_mgr.dependencies["users"]
    stats_mgr = StatisticsManager()
    stats_mgr.update_statistics("users", "row_count", 500)
    assert stats_mgr.get_statistics("users", "row_count") == 500
    
    metadata_mgr = MetadataManager()
    assert metadata_mgr is not None



