from dbms.database_object.data_type_manager import DataTypeManager
from dbms.database_object.data_type import DataType
from unittest.mock import Mock


def test_data_type_manager_can_be_created():
    # Arrange
    data_types = {}
    manager = DataTypeManager(data_types)

    # Assert
    assert manager.data_types is data_types
    assert callable(manager.register_data_type)
    assert callable(manager.validate_value)
    assert callable(manager.convert_value)
    assert callable(manager.resolve_data_type)


def test_register_data_type():
    # Arrange
    manager = DataTypeManager({})
    data_type = DataType("INT", lambda value: True, int)

    # Act
    result = manager.register_data_type("INT", data_type)

    # Assert
    assert result is True
    assert manager.data_types["INT"] is data_type


def test_validate_value():
    # Arrange
    data_type = Mock(spec=DataType)
    data_type.validate.return_value = True
    manager = DataTypeManager({"INT": data_type})

    # Act
    result = manager.validate_value(10, "INT")

    # Assert
    assert result is True
    data_type.validate.assert_called_once_with(10)


def test_convert_value():
    # Arrange
    data_type = Mock(spec=DataType)
    data_type.convert.return_value = 10
    manager = DataTypeManager({"INT": data_type})

    # Act
    result = manager.convert_value("10", "INT")

    # Assert
    assert result == 10
    data_type.convert.assert_called_once_with("10")


def test_resolve_data_type():
    # Arrange
    data_type = DataType("INT", lambda value: True, int)
    manager = DataTypeManager({"INT": data_type})

    # Act
    result = manager.resolve_data_type("INT")

    # Assert
    assert result is data_type
