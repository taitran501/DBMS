from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

@dataclass(frozen=True)
class DataTypeDescriptor:
    name: str
    python_type: type = object
    nullable: bool = True
    length: int | None = None
    precision: int | None = None
    scale: int | None = None

class TypeValidator:
    TYPES = {"INT": int, "TEXT": str, "BOOLEAN": bool, "FLOAT": float, "DECIMAL": Decimal, "DATE": date, "DATETIME": datetime}
    def validate_type_value(self, type_name, value):
        expected = self.TYPES.get(type_name.upper())
        return True if expected is None else isinstance(value, expected)

class TypeConverter:
    def convert_type_value(self, type_name, value):
        name = type_name.upper()
        if name == "INT" and isinstance(value, str):
            try: return int(value)
            except ValueError: return value
        if name == "TEXT" and value is not None and not isinstance(value, str): return str(value)
        if name == "BOOLEAN" and isinstance(value, str) and value.lower() in {"true", "false"}: return value.lower() == "true"
        if name == "FLOAT" and isinstance(value, str):
            try: return float(value)
            except ValueError: return value
        if name == "DECIMAL" and isinstance(value, str):
            try: return Decimal(value)
            except InvalidOperation: return value
        if name == "DATE" and isinstance(value, str):
            try: return date.fromisoformat(value)
            except ValueError: return value
        if name == "DATETIME" and isinstance(value, str):
            try: return datetime.fromisoformat(value)
            except ValueError: return value
        return value

class DataType:
    def __init__(self, name, validator=None, converter=None):
        self.descriptor = name if isinstance(name, DataTypeDescriptor) else DataTypeDescriptor(name)
        self.name = self.descriptor.name; self.validator = validator or TypeValidator(); self.converter = converter or TypeConverter()

class DataTypeManager:
    def __init__(self):
        self.types = {}; self._validator = TypeValidator(); self._converter = TypeConverter()
        for name in ("INT", "TEXT", "BOOLEAN"): self.register_type(DataTypeDescriptor(name, TypeValidator.TYPES[name]))
    def register_type(self, descriptor):
        name = descriptor.name.upper()
        if name in self.types: raise ValueError(f"Data type {name} already exists")
        self.types[name] = DataType(descriptor, self._validator, self._converter); return self.types[name]
    def resolve(self, name):
        if name.upper() not in self.types: raise ValueError(f"Data type {name} is not registered")
        return self.types[name.upper()]
    def validate_value(self, data_type, value):
        if value is None: return data_type.descriptor.nullable
        if data_type.descriptor.python_type is not object and not isinstance(value, data_type.descriptor.python_type): return False
        descriptor = data_type.descriptor
        if descriptor.length is not None and isinstance(value, str) and len(value) > descriptor.length: return False
        if descriptor.precision is not None and isinstance(value, Decimal):
            digits = len(value.as_tuple().digits)
            scale = max(-value.as_tuple().exponent, 0)
            if digits > descriptor.precision or (descriptor.scale is not None and scale > descriptor.scale): return False
        if data_type.descriptor.python_type is not object: return True
        return data_type.validator.validate_type_value(data_type.name, value)
    def convert_value(self, data_type, value): return data_type.converter.convert_type_value(data_type.name, value)
    def make_descriptor(self, name, *, nullable=True, length=None, precision=None, scale=None):
        normalized = name.upper()
        if normalized == "VARCHAR": return DataTypeDescriptor(normalized, str, nullable, length=length)
        return DataTypeDescriptor(normalized, TypeValidator.TYPES.get(normalized, object), nullable, precision=precision, scale=scale)
