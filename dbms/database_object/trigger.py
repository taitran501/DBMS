from collections.abc import Callable


class Trigger:
    def __init__(
        self,
        name: str,
        event: str,
        table_name: str,
        callback: Callable[[object], object],
    ) -> None:
        self.name = name
        self.event = event
        self.table_name = table_name
        self.callback = callback

    def fire(self, row: object) -> bool:
        return False
