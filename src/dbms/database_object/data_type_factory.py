from abc import ABC, abstractmethod

from dbms.database_object.data_type import DataType


class DataTypeFactory(ABC):
    """Creator interface for constructing a configured DataType product."""

    @abstractmethod
    def create_data_type(self) -> DataType:
        """Create the concrete data type selected by this factory."""


class IntegerDataTypeFactory(DataTypeFactory):
    """Concrete creator for integer data types."""

    def create_data_type(self) -> DataType:
        return DataType(
            "INT",
            lambda value: isinstance(value, int) and not isinstance(value, bool),
            int,
        )


class FloatDataTypeFactory(DataTypeFactory):
    """Concrete creator for floating-point data types."""

    def create_data_type(self) -> DataType:
        return DataType("FLOAT", lambda value: isinstance(value, float), float)


class TextDataTypeFactory(DataTypeFactory):
    """Concrete creator for text data types."""

    def create_data_type(self) -> DataType:
        return DataType("TEXT", lambda value: isinstance(value, str), str)
