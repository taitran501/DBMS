from dbms.database_object.data_type import DataType
from unittest.mock import Mock


def test_data_type_can_be_created():
    # Arrange
    validator = lambda value: True
    converter = lambda value: value
    data_type = DataType("INT", validator, converter)

    # Assert
    assert data_type.name == "INT"
    assert data_type.validator is validator
    assert data_type.converter is converter
    assert callable(data_type.validate)
    assert callable(data_type.convert)


def test_validate():
    # Arrange
    validator = Mock(return_value=True)
    data_type = DataType("POSITIVE_INT", validator, int)

    # Act
    result = data_type.validate(10)

    # Assert
    assert result is True
    validator.assert_called_once_with(10)


def test_convert():
    # Arrange
    converter = Mock(return_value=10)
    data_type = DataType("INT", lambda value: True, converter)

    # Act
    result = data_type.convert("10")

    # Assert
    assert result == 10
    converter.assert_called_once_with("10")
