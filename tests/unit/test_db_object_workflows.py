import pytest
from dbms.subsystems import DatabaseObjectManager
from dbms.database_object.metadata_management.system_catalog import Catalog, MetadataManager
from dbms.database_object.index_management.index_manager import IndexManager
from dbms.database_object.database_management.database_manager import DatabaseManager
from dbms.database_object.schema_management.schema_manager import SchemaManager
from dbms.database_object.schema_management.schema import TableSchema, ColumnSchema
from dbms.database_object.table_management.table_manager import TableManager, TableOrganization, TableScope

@pytest.fixture
def db_object_manager():
    catalog = Catalog()
    index_manager = IndexManager()
    metadata_manager = MetadataManager(catalog)
    return DatabaseObjectManager(
        catalog=catalog,
        index_manager=index_manager,
        metadata_manager=metadata_manager
    )

def test_provision_database_and_schema_registers_retrievable_objects(db_object_manager):
    """
    Test the Database & Schema Provisioning workflow.
    """
    db_manager = db_object_manager.database_manager
    schema_manager = db_object_manager.schema_manager

    # 1. Create Database
    db = db_manager.create_database("test_db")
    assert db.name == "test_db"
    assert db_manager.get_database("test_db") == db

    # 2. Create Schema
    schema = schema_manager.create_schema("test_db", "public")
    assert schema.name == "public"
    assert schema.descriptor.name == "public"
    assert schema_manager.get_schema("test_db", "public") == schema

def test_define_table_registers_descriptor_columns_and_lookup(db_object_manager):
    """
    Test the core DDL flow for creating a Table.
    """
    table_manager = db_object_manager.table_manager
    
    # Define a TableSchema
    schema = TableSchema(
        name="users",
        columns=[
            ColumnSchema("id", "INT"),
            ColumnSchema("name", "TEXT")
        ]
    )

    # 1. Create Table
    table = table_manager.create_table("public", "users", schema)
    
    assert table.name == "users"
    assert table.descriptor.organization == TableOrganization.HEAP
    assert table.descriptor.scope == TableScope.PERSISTENT
    assert len(table.descriptor.columns) == 2
    assert table.descriptor.columns[0].name == "id"
    assert table.descriptor.columns[1].data_type == "TEXT"

    # Verify retrieval
    retrieved_table = table_manager.get_table("public", "users")
    assert retrieved_table == table

def test_validate_and_convert_data_types_returns_contract_results(db_object_manager):
    """
    Test DataType resolution and validation.
    """
    data_type_manager = db_object_manager.data_type_manager
    
    # The default types INT, TEXT, BOOLEAN should be loaded
    assert "INT" in data_type_manager.types
    
    int_type = data_type_manager.types["INT"]
    
    # Test validation
    assert data_type_manager.validate_value(int_type, 123) is True
    assert data_type_manager.validate_value(int_type, "123") is False # It's a string, validation fails before conversion
    
    # Test conversion
    converted = data_type_manager.convert_value(int_type, "456")
    assert converted == 456
    
def test_create_view_procedure_and_trigger_registers_retrievable_objects(db_object_manager):
    """
    Test View, Stored Procedure, and Trigger creation workflows.
    """
    view_manager = db_object_manager.view_manager
    proc_manager = db_object_manager.stored_procedure_manager
    trigger_manager = db_object_manager.trigger_manager
    
    # Create View
    view = view_manager.create_view("public", "active_users", "SELECT * FROM users WHERE active = 1")
    assert view.descriptor.name == "active_users"
    
    # Create Procedure
    proc = proc_manager.create_procedure("public", "archive_users", [], "DELETE FROM users WHERE active = 0")
    assert proc.descriptor.name == "archive_users"
    
    # Create Trigger
    trigger = trigger_manager.create_trigger("public", "after_insert_user", "users", "INSERT", "EXECUTE archive_users")
    assert trigger.name == "after_insert_user"

def test_create_index_constraint_and_relationship_registers_retrievable_objects(db_object_manager):
    from dbms.database_object.index_management.index_manager import Index
    from dbms.database_object.constraint_management.constraint_manager import Constraint
    from dbms.database_object.relationship_management.relationship_manager import Relationship
    
    idx_manager = db_object_manager.index_manager
    constraint_manager = db_object_manager.constraint_manager
    rel_manager = db_object_manager.relationship_manager
    
    # 1. Create Index
    index = Index("idx_users_name", "B_TREE", ["name"], False)
    idx_manager.create_index("users", index)
    retrieved_idx = idx_manager.get_index("users", "idx_users_name")
    assert retrieved_idx.name == "idx_users_name"
    
    # 2. Create Constraint
    constraint = Constraint("pk_users", "PRIMARY_KEY", ["id"])
    constraint_manager.create_constraint("users", constraint)
    retrieved_constraint = constraint_manager.get_constraint("users", "pk_users")
    assert retrieved_constraint.name == "pk_users"
    
    # 3. Create Relationship
    relationship = Relationship("fk_users_profile", "users", "profiles", "ONE_TO_ONE")
    rel_manager.create_relationship(relationship)
    retrieved_rel = rel_manager.get_relationship("fk_users_profile")
    assert retrieved_rel.name == "fk_users_profile"
