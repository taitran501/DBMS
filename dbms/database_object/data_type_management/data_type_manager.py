from typing import Union, Optional

class DataTypeDescriptor:
    def __init__(self, name: str):
        self.name = name

class TypeValidator:
    def validate(self, type_name: str, value) -> bool:
        if type_name == "INT":
            return isinstance(value, int)
        if type_name == "TEXT":
            return isinstance(value, str)
        if type_name == "BOOLEAN":
            return isinstance(value, bool)
        return True

class TypeConverter:
    def convert(self, type_name: str, value):
        if type_name == "INT" and isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                pass
        return value

class DataType:
    def __init__(self, name: Union[str, DataTypeDescriptor], validator: Optional[TypeValidator] = None, converter: Optional[TypeConverter] = None):
        if isinstance(name, DataTypeDescriptor):
            self.descriptor = name
        else:
            self.descriptor = DataTypeDescriptor(name)
        
        self.name = self.descriptor.name
        self.validator = validator or TypeValidator()
        self.converter = converter or TypeConverter()

class DataTypeManager:
    def __init__(self):
        self.types: dict[str, DataType] = {}
        self._validator = TypeValidator()
        self._converter = TypeConverter()
        self._initialize_default_types()

    def _initialize_default_types(self) -> None:
        default_types = ["INT", "TEXT", "BOOLEAN"]
        for name in default_types:
            self.types[name] = DataType(name, self._validator, self._converter)

    def validate_value(self, data_type: DataType, value) -> bool:
        return data_type.validator.validate(data_type.name, value)

    def convert_value(self, data_type: DataType, value):
        return data_type.converter.convert(data_type.name, value)
