from collections.abc import Callable

from dbms.database_object.exceptions import TriggerError


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
        """Notify this trigger's callback about a row event.

        Callbacks commonly return ``None`` after performing a side effect.  An
        explicit ``False`` is therefore the only callback result treated as a
        rejected dispatch.
        """
        try:
            result = self.callback(row)
        except Exception as error:
            raise TriggerError(f"Trigger '{self.name}' callback failed") from error
        return result is not False
