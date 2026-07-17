from dbms.database_object.data_type import DataType


def test_data_type_stores_name_validator_and_converter():
    validator = lambda value: True
    converter = lambda value: value
    data_type = DataType("INT", validator, converter)

    assert data_type.name == "INT"
    assert data_type.validator is validator
    assert data_type.converter is converter


def test_data_type_exposes_validate_method():
    data_type = DataType("INT", lambda value: True, int)

    assert callable(data_type.validate)


def test_data_type_exposes_convert_method():
    data_type = DataType("INT", lambda value: True, int)

    assert callable(data_type.convert)
