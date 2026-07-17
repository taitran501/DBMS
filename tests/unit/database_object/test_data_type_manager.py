from dbms.database_object.data_type_manager import DataTypeManager

def test_register_data_type():
    pass

def test_validate_value():
    pass

def test_convert_value():
    pass

def test_reject_invalid_value():
    pass

def test_reject_invalid_conversion():
    pass

def test_resolve_data_type():
    pass

def test_data_type_manager_can_be_created():
    data_types = {}
    manager = DataTypeManager(data_types)

    assert manager.data_types is data_types
    assert callable(manager.register_data_type)
    assert callable(manager.validate_value)
    assert callable(manager.convert_value)
    assert callable(manager.resolve_data_type)
