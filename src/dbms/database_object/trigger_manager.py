from collections.abc import Callable

from dbms.database_object.exceptions import DuplicateTriggerError
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
        if any(
            trigger.name == name
            for registered_triggers in self.triggers.values()
            for trigger in registered_triggers
        ):
            raise DuplicateTriggerError(f"Trigger '{name}' already exists")

        trigger = Trigger(name, event, table_name, callback)
        self.triggers.setdefault(event, []).append(trigger)
        return trigger

    def drop_trigger(self, name: str) -> bool:
        for registered_triggers in self.triggers.values():
            for trigger in registered_triggers:
                if trigger.name == name:
                    registered_triggers.remove(trigger)
                    return True
        return False

    def bind_event(self, event: str, callback: Callable[[object], object]) -> bool:
        registered_triggers = self.triggers.get(event, [])
        for trigger in registered_triggers:
            trigger.callback = callback
        return bool(registered_triggers)

    def execute_triggers(self, event: str, row: object) -> bool:
        for trigger in self.triggers.get(event, []):
            if not trigger.fire(row):
                return False
        return True
