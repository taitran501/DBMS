from dbms.database_object.column import Column
from dbms.database_object.data_type import DataType


def test_column_can_be_created():
    data_type = DataType("INT", lambda value: True, int)
    column = Column("c1", "age", data_type, nullable=True)

    assert column.column_id == "c1"
    assert column.name == "age"
    assert column.data_type is data_type
    assert column.nullable is True
    assert callable(column.validate)


def test_validate():
    pass
