from dbms.database_object.data_type import DataType


def test_data_type_can_be_created():
    validator = lambda value: True
    converter = lambda value: value
    data_type = DataType("INT", validator, converter)

    assert data_type.name == "INT"
    assert data_type.validator is validator
    assert data_type.converter is converter
    assert callable(data_type.validate)
    assert callable(data_type.convert)


def test_validate():
    validator = lambda value: value > 0
    data_type = DataType("POSITIVE_INT", validator, int)

    result = data_type.validate(10)

    assert result is True


def test_convert():
    data_type = DataType("INT", lambda value: True, int)

    result = data_type.convert("10")

    assert result == 10
