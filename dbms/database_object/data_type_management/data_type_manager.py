from dataclasses import dataclass

@dataclass(frozen=True)
class DataTypeDescriptor:
    name: str
    python_type: type = object
    nullable: bool = True

class TypeValidator:
    TYPES = {"INT": int, "TEXT": str, "BOOLEAN": bool}
    def validate(self, type_name, value):
        expected = self.TYPES.get(type_name.upper())
        return True if expected is None else isinstance(value, expected)

class TypeConverter:
    def convert(self, type_name, value):
        name = type_name.upper()
        if name == "INT" and isinstance(value, str):
            try: return int(value)
            except ValueError: return value
        if name == "TEXT" and value is not None and not isinstance(value, str): return str(value)
        if name == "BOOLEAN" and isinstance(value, str) and value.lower() in {"true", "false"}: return value.lower() == "true"
        return value

class DataType:
    def __init__(self, name, validator=None, converter=None):
        self.descriptor = name if isinstance(name, DataTypeDescriptor) else DataTypeDescriptor(name)
        self.name = self.descriptor.name; self.validator = validator or TypeValidator(); self.converter = converter or TypeConverter()

class DataTypeManager:
    def __init__(self):
        self.types = {}; self._validator = TypeValidator(); self._converter = TypeConverter()
        for name, py_type in TypeValidator.TYPES.items(): self.register_type(DataTypeDescriptor(name, py_type))
    def register_type(self, descriptor):
        name = descriptor.name.upper()
        if name in self.types: raise ValueError(f"Data type {name} already exists")
        self.types[name] = DataType(descriptor, self._validator, self._converter); return self.types[name]
    def resolve(self, name):
        if name.upper() not in self.types: raise ValueError(f"Data type {name} is not registered")
        return self.types[name.upper()]
    def validate_value(self, data_type, value):
        if value is None: return data_type.descriptor.nullable
        if data_type.descriptor.python_type is not object: return isinstance(value, data_type.descriptor.python_type)
        return data_type.validator.validate(data_type.name, value)
    def convert_value(self, data_type, value): return data_type.converter.convert(data_type.name, value)
