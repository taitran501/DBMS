from collections.abc import Callable

from dbms.database_object.trigger import Trigger


class TriggerManager:
    def __init__(self, triggers: dict[str, list[Trigger]] | None = None) -> None:
        self.triggers = {} if triggers is None else triggers

    def create_trigger(
        self,
        name: str,
        event: str,
        table_name: str,
        callback: Callable[[object], object],
    ) -> Trigger:
        return None

    def drop_trigger(self, name: str) -> bool:
        return False

    def bind_event(self, event: str, callback: Callable[[object], object]) -> bool:
        return False

    def execute_triggers(self, event: str, row: object) -> bool:
        return False
