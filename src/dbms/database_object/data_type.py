from collections.abc import Callable


class DataType:
    def __init__(
        self,
        name: str,
        validator: Callable[[object], bool],
        converter: Callable[[object], object],
    ) -> None:
        self.name = name
        self.validator = validator
        self.converter = converter

    def validate(self, value: object) -> bool:
        return bool(self.validator(value))

    def convert(self, value: object) -> object:
        return self.converter(value)
