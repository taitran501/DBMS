from dataclasses import dataclass
from typing import Callable, Optional
from dbms.errors import TriggerNotExecutableError

@dataclass(frozen=True)
class TriggerDescriptor:
    name: str
    event: str
    timing: str
    action: object

@dataclass(frozen=True)
class TriggerEventBinding:
    trigger_name: str
    event: str

class TriggerExecutor:
    def execute_trigger_action(self, descriptor, context=None):
        if callable(descriptor.action): return descriptor.action(context or {})
        raise TriggerNotExecutableError(f"Trigger {descriptor.name} has no executable action")

class Trigger:
    def __init__(self, name, event=None, timing=None, action=None, binding=None, executor=None):
        self.descriptor = name if isinstance(name, TriggerDescriptor) else TriggerDescriptor(name, event or "", timing or "", action or "")
        self.name = self.descriptor.name; self.event = self.descriptor.event; self.timing = self.descriptor.timing; self.action = self.descriptor.action
        self.binding = binding or TriggerEventBinding(self.name, self.event); self.executor = executor or TriggerExecutor()

class TriggerManager:
    def __init__(self): self.triggers = {}
    def create_trigger(self, table_name, name, event, timing, action):
        event, timing = event.upper(), timing.upper()
        if event not in {"INSERT", "UPDATE", "DELETE"} and timing in {"INSERT", "UPDATE", "DELETE"}:
            event, timing = timing, "AFTER"  # legacy: schema, name, table, event, action
        if event not in {"INSERT", "UPDATE", "DELETE"}: raise ValueError(f"Unsupported trigger event {event}")
        if timing not in {"BEFORE", "AFTER"}: raise ValueError(f"Unsupported trigger timing {timing}")
        items = self.triggers.setdefault(table_name, [])
        if any(t.name == name for t in items): raise ValueError(f"Trigger {name} already exists on table {table_name}")
        trigger = Trigger(name, event, timing, action); items.append(trigger); return trigger
    def drop_trigger(self, table_name, name):
        if table_name in self.triggers: self.triggers[table_name] = [t for t in self.triggers[table_name] if t.name != name]
    def get_trigger(self, table_name, name):
        for trigger in self.triggers.get(table_name, []):
            if trigger.name == name: return trigger
        raise ValueError(f"Trigger {name} not found on table {table_name}")
    def publish_table_event(self, table_name, event, timing=None, context=None):
        event = event.upper(); timing = timing.upper() if timing else None
        matched = [t for t in self.triggers.get(table_name, []) if t.binding.event.upper() == event and (timing is None or t.timing.upper() == timing)]
        for trigger in matched:
            try: trigger.executor.execute_trigger_action(trigger.descriptor, context)
            except TypeError: trigger.executor.execute_trigger_action(trigger.descriptor)
        return matched
