import pytest
from dbms.subsystems import DatabaseObjectManager
from dbms.database_object.metadata_management.system_catalog import Catalog, MetadataManager
from dbms.database_object.index_management.index_manager import IndexManager, Index
from dbms.database_object.constraint_management.constraint_manager import Constraint
from dbms.database_object.relationship_management.relationship_manager import Relationship
from dbms.database_object.schema_management.schema import TableSchema, ColumnSchema

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

def test_duplicate_entities_raise_value_error(db_object_manager):
    db_manager = db_object_manager.database_manager
    schema_manager = db_object_manager.schema_manager
    table_manager = db_object_manager.table_manager
    view_manager = db_object_manager.view_manager
    proc_manager = db_object_manager.stored_procedure_manager
    
    # DB
    db_manager.create_database("db1")
    with pytest.raises(ValueError, match="already exists"):
        db_manager.create_database("db1")
        
    # Schema
    schema_manager.create_schema("db1", "schema1")
    with pytest.raises(ValueError, match="already exists"):
        schema_manager.create_schema("db1", "schema1")
        
    # Table
    schema = TableSchema(name="t1", columns=[ColumnSchema("c1", "INT")])
    table_manager.create_table("schema1", "t1", schema)
    with pytest.raises(ValueError, match="already exists"):
        table_manager.create_table("schema1", "t1", schema)
        
    # View
    view_manager.create_view("schema1", "v1", "SELECT *")
    with pytest.raises(ValueError, match="already exists"):
        view_manager.create_view("schema1", "v1", "SELECT *")
        
    # Procedure
    proc_manager.create_procedure("schema1", "p1", [], "BODY")
    with pytest.raises(ValueError, match="already exists"):
        proc_manager.create_procedure("schema1", "p1", [], "BODY")

def test_missing_entities_raise_value_error(db_object_manager):
    db_manager = db_object_manager.database_manager
    schema_manager = db_object_manager.schema_manager
    table_manager = db_object_manager.table_manager
    
    with pytest.raises(ValueError, match="not found"):
        db_manager.get_database("missing_db")
        
    with pytest.raises(ValueError, match="not found"):
        schema_manager.get_schema("db1", "missing_schema")
        
    with pytest.raises(ValueError, match="not found"):
        table_manager.get_table("schema1", "missing_table")
        
def test_schema_create_and_drop_raise_permission_error_when_policy_denies(db_object_manager, monkeypatch):
    schema_manager = db_object_manager.schema_manager
    db_manager = db_object_manager.database_manager
    db_manager.create_database("db1")
    
    # Mock policy to simulate guest user rejection
    def mock_can_create_schema(actor_id, db_id):
        return False
    def mock_can_drop_schema(actor_id, schema_id):
        return False
        
    monkeypatch.setattr(schema_manager._ownership_policy, "can_create_schema", mock_can_create_schema)
    monkeypatch.setattr(schema_manager._ownership_policy, "can_drop_schema", mock_can_drop_schema)
    
    with pytest.raises(PermissionError, match="Schema creation rejected by policy"):
        schema_manager.create_schema("db1", "schema1")
        
    # Temporarily allow creation so we can test drop
    monkeypatch.setattr(schema_manager._ownership_policy, "can_create_schema", lambda a, b: True)
    schema_manager.create_schema("db1", "schema2")
    
    with pytest.raises(PermissionError, match="Schema deletion rejected by policy"):
        schema_manager.drop_schema("db1", "schema2")

def test_extended_object_managers_reject_duplicate_and_missing_objects(db_object_manager):
    idx_manager = db_object_manager.index_manager
    constraint_manager = db_object_manager.constraint_manager
    rel_manager = db_object_manager.relationship_manager
    
    index = Index("idx1", "B_TREE", ["c1"], False)
    idx_manager.create_index("t1", index)
    
    with pytest.raises(ValueError, match="already exists"):
        idx_manager.create_index("t1", index)
        
    with pytest.raises(ValueError, match="not found"):
        idx_manager.get_index("t1", "missing_idx")
        
    constraint = Constraint("c1", "PRIMARY_KEY", ["col"])
    constraint_manager.create_constraint("t1", constraint)
    
    with pytest.raises(ValueError, match="already exists"):
        constraint_manager.create_constraint("t1", constraint)
        
    with pytest.raises(ValueError, match="not found"):
        constraint_manager.get_constraint("t1", "missing_constraint")
        
    rel = Relationship("r1", "t1", "t2", "1-N")
    rel_manager.create_relationship(rel)
    
    with pytest.raises(ValueError, match="already exists"):
        rel_manager.create_relationship(rel)
        
    with pytest.raises(ValueError, match="not found"):
        rel_manager.get_relationship("missing_rel")

def test_datatype_conversion_preserves_invalid_input_and_validation_checks_python_types(db_object_manager):
    data_type_manager = db_object_manager.data_type_manager
    
    int_type = data_type_manager.types["INT"]
    
    # Edge case: convert invalid string to INT
    converted = data_type_manager.convert_value(int_type, "abc")
    assert converted == "abc"  # As per implementation, if ValueError occurs it returns the original value
    
    # Test text validation
    text_type = data_type_manager.types["TEXT"]
    assert data_type_manager.validate_value(text_type, 123) is False
    assert data_type_manager.validate_value(text_type, "abc") is True
    
    # Test boolean validation
    bool_type = data_type_manager.types["BOOLEAN"]
    assert data_type_manager.validate_value(bool_type, "True") is False
    assert data_type_manager.validate_value(bool_type, True) is True
    
    # Unregistered type fallback
    # The validator returns True for unknown types
    assert data_type_manager._validator.validate_type_value("UNKNOWN_TYPE", 123) is True
    
def test_drop_methods_ignore_or_reject_missing_objects_by_contract(db_object_manager):
    idx_manager = db_object_manager.index_manager
    constraint_manager = db_object_manager.constraint_manager
    rel_manager = db_object_manager.relationship_manager
    
    # Dropping non-existent elements should not raise error, or should silently pass based on implementation
    idx_manager.drop_index("t1", "missing_idx")  # table t1 doesn't even exist
    constraint_manager.drop_constraint("t1", "missing_constraint")
    rel_manager.drop_relationship("missing_rel")
    
def test_drop_then_get_raises_not_found_for_registered_objects(db_object_manager):
    db_manager = db_object_manager.database_manager
    view_manager = db_object_manager.view_manager
    proc_manager = db_object_manager.stored_procedure_manager
    trigger_manager = db_object_manager.trigger_manager
    
    # Database
    db_manager.create_database("db2")
    db_manager.drop_database("db2")
    with pytest.raises(ValueError, match="not found"):
        db_manager.get_database("db2")
    db_manager.drop_database("db2") # Drop missing
    
    # View
    view_manager.create_view("schema1", "v2", "SELECT 1")
    view_manager.drop_view("schema1", "v2")
    with pytest.raises(ValueError, match="not found"):
        view_manager.get_view("schema1", "v2")
    view_manager.drop_view("schema1", "v2") # Drop missing
    
    # Procedure
    proc_manager.create_procedure("schema1", "p2", [], "BODY")
    proc_manager.drop_procedure("schema1", "p2")
    with pytest.raises(ValueError, match="not found"):
        proc_manager.get_procedure("schema1", "p2")
    proc_manager.drop_procedure("schema1", "p2") # Drop missing
    
    # Trigger
    trigger_manager.create_trigger("schema1", "trig1", "t1", "INSERT", "EXECUTE a")
    trigger_manager.drop_trigger("schema1", "trig1")
    with pytest.raises(ValueError, match="not found"):
        trigger_manager.get_trigger("schema1", "trig1")
    trigger_manager.drop_trigger("schema1", "trig1") # Drop missing
