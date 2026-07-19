from dbms.database_object.column import Column
from dbms.database_object.data_type import DataType
from unittest.mock import Mock


def test_column_can_be_created():
    # Arrange
    data_type = DataType("INT", lambda value: True, int)
    column = Column("c1", "age", data_type, nullable=True)

    # Assert
    assert column.column_id == "c1"
    assert column.name == "age"
    assert column.data_type is data_type
    assert column.nullable is True
    assert callable(column.validate)


def test_validate():
    # Arrange
    data_type = Mock(spec=DataType)
    data_type.validate.return_value = True
    column = Column("c1", "age", data_type)

    # Act
    result = column.validate(25)

    # Assert
    assert result is True
    data_type.validate.assert_called_once_with(25)


def test_validate_nullable():
    nullable_column = Column("c1", "age", Mock(spec=DataType), nullable=True)
    required_column = Column("c2", "age", Mock(spec=DataType), nullable=False)

    assert nullable_column.validate(None) is True
    assert required_column.validate(None) is False


def test_validate_length():
    column = Column("c1", "name", Mock(spec=DataType))

    assert column.validate_length("Ada", 3) is True
    assert column.validate_length("Grace", 3) is False


def test_validate_precision():
    column = Column("c1", "amount", Mock(spec=DataType))

    assert column.validate_precision("12.34", 2) is True
    assert column.validate_precision("12.345", 2) is False


def test_apply_default_value():
    column = Column("c1", "status", Mock(spec=DataType))

    assert column.apply_default_value(None, "pending") == "pending"
    assert column.apply_default_value("active", "pending") == "active"


def test_generate_identity():
    column = Column("c1", "id", Mock(spec=DataType))
    generator = Mock(return_value=42)

    assert column.generate_identity(generator) == 42
    generator.assert_called_once_with()


def test_evaluate_computed_column():
    column = Column("c1", "total", Mock(spec=DataType))
    values = {"quantity": 3, "unit_price": 12}
    expression = Mock(return_value=36)

    assert column.evaluate_computed_column(values, expression) == 36
    expression.assert_called_once_with(values)
