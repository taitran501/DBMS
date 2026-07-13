from dataclasses import dataclass
from typing import Callable, Optional
from dbms.errors import ProcedureNotExecutableError

@dataclass(frozen=True)
class ProcedureDescriptor:
    name: str
    parameters: tuple[str, ...]
    body: object

class ProcedureExecutor:
    def __init__(self, strict=False): self.strict = strict
    def execute(self, descriptor, args):
        if not callable(descriptor.body):
            if self.strict: raise ProcedureNotExecutableError(f"Procedure {descriptor.name} has no executable body")
            return descriptor.body
        if len(args) != len(descriptor.parameters): raise ValueError(f"Procedure {descriptor.name} expects {len(descriptor.parameters)} arguments")
        return descriptor.body(*args)

class StoredProcedure:
    def __init__(self, name, parameters=None, body=None, executor=None):
        self.descriptor = name if isinstance(name, ProcedureDescriptor) else ProcedureDescriptor(name, tuple(parameters or ()), body if body is not None else "")
        self.name = self.descriptor.name; self.parameters = list(self.descriptor.parameters); self.body = self.descriptor.body; self.executor = executor or ProcedureExecutor()

class StoredProcedureManager:
    def __init__(self): self.procedures = {}
    def create_procedure(self, database_name, proc_name, parameters, body):
        group = self.procedures.setdefault(database_name, {})
        if proc_name in group: raise ValueError(f"Procedure {proc_name} already exists in database {database_name}")
        group[proc_name] = StoredProcedure(proc_name, parameters, body, ProcedureExecutor(strict=True)); return group[proc_name]
    def drop_procedure(self, database_name, proc_name):
        if database_name in self.procedures: self.procedures[database_name].pop(proc_name, None)
    def get_procedure(self, database_name, proc_name):
        try: return self.procedures[database_name][proc_name]
        except KeyError as exc: raise ValueError(f"Procedure {proc_name} not found in database {database_name}") from exc
    def execute_procedure(self, database_name, proc_name, arguments):
        proc = self.get_procedure(database_name, proc_name); return proc.executor.execute(proc.descriptor, list(arguments))
