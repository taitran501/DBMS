from typing import Union, Optional

class TriggerDescriptor:
    def __init__(self, name: str, event: str, timing: str, action: str):
        self.name = name
        self.event = event      # e.g., INSERT, UPDATE, DELETE
        self.timing = timing    # e.g., BEFORE, AFTER
        self.action = action    # Action details or procedure to execute

class TriggerEventBinding:
    def __init__(self, trigger_name: str, event: str):
        self.trigger_name = trigger_name
        self.event = event

class TriggerExecutor:
    def __init__(self):
        pass

    def execute(self, descriptor: TriggerDescriptor) -> None:
        # Placeholder execution logic
        pass

class Trigger:
    def __init__(self, name: Union[str, TriggerDescriptor], event: Optional[str] = None, timing: Optional[str] = None, action: Optional[str] = None, binding: Optional[TriggerEventBinding] = None, executor: Optional[TriggerExecutor] = None):
        if isinstance(name, TriggerDescriptor):
            self.descriptor = name
        else:
            self.descriptor = TriggerDescriptor(name, event or "", timing or "", action or "")
        
        self.name = self.descriptor.name
        self.event = self.descriptor.event
        self.timing = self.descriptor.timing
        self.action = self.descriptor.action
        self.binding = binding or TriggerEventBinding(self.name, self.event)
        self.executor = executor or TriggerExecutor()

class TriggerManager:
    def __init__(self):
        # table_name -> list of Trigger objects
        self.triggers: dict[str, list[Trigger]] = {}

    def create_trigger(self, table_name: str, name: str, event: str, timing: str, action: str) -> Trigger:
        if table_name not in self.triggers:
            self.triggers[table_name] = []
        if any(t.name == name for t in self.triggers[table_name]):
            raise ValueError(f"Trigger {name} already exists on table {table_name}")
        
        descriptor = TriggerDescriptor(name, event, timing, action)
        trigger = Trigger(descriptor)
        self.triggers[table_name].append(trigger)
        return trigger

    def drop_trigger(self, table_name: str, name: str) -> None:
        if table_name in self.triggers:
            self.triggers[table_name] = [t for t in self.triggers[table_name] if t.name != name]

    def get_trigger(self, table_name: str, name: str) -> Trigger:
        if table_name in self.triggers:
            for t in self.triggers[table_name]:
                if t.name == name:
                    return t
        raise ValueError(f"Trigger {name} not found on table {table_name}")

    def publish_table_event(self, table_name: str, event: str, timing: Optional[str] = None) -> list[Trigger]:
        event = event.upper()
        timing = timing.upper() if timing else None
        matched = [
            trigger for trigger in self.triggers.get(table_name, [])
            if trigger.binding.event.upper() == event
            and (timing is None or trigger.timing.upper() == timing)
        ]
        for trigger in matched:
            trigger.executor.execute(trigger.descriptor)
        return matched
