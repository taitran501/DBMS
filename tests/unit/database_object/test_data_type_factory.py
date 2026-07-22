import pytest

from dbms.database_object.data_type_factory import (
    FloatDataTypeFactory,
    IntegerDataTypeFactory,
    TextDataTypeFactory,
)


@pytest.mark.parametrize(
    ("factory", "raw_value", "expected_value", "invalid_value", "expected_name"),
    [
        (IntegerDataTypeFactory(), "42", 42, "forty-two", "INT"),
        (FloatDataTypeFactory(), "3.5", 3.5, "three point five", "FLOAT"),
        (TextDataTypeFactory(), 42, "42", 42, "TEXT"),
    ],
)
def test_factory_creates_the_data_type_it_selects(
    factory, raw_value, expected_value, invalid_value, expected_name
):
    # Act
    data_type = factory.create_data_type()

    # Assert
    assert data_type.name == expected_name
    assert data_type.convert(raw_value) == expected_value
    assert data_type.validate(expected_value) is True
    assert data_type.validate(invalid_value) is False
