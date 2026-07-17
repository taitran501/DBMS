from dbms.database_object.data_type import DataType


class DataTypeManager:
    def __init__(self, data_types: dict[str, DataType] | None = None) -> None:
        self.data_types = {} if data_types is None else data_types

    def register_data_type(self, name: str, data_type: DataType) -> bool:
        return False

    def validate_value(self, value: object, data_type_name: str) -> bool:
        return False

    def convert_value(self, value: object, data_type_name: str) -> object:
        return None

    def resolve_data_type(self, name: str) -> DataType:
        return None
