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
