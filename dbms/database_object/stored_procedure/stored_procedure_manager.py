from typing import Union, Optional

class ProcedureDescriptor:
    def __init__(self, name: str, parameters: list[str], body: str):
        self.name = name
        self.parameters = parameters
        self.body = body

class ProcedureExecutor:
    def __init__(self):
        pass

    def execute(self, descriptor: ProcedureDescriptor, args: list) -> None:
        # Placeholder execution logic
        pass

class StoredProcedure:
    def __init__(self, name: Union[str, ProcedureDescriptor], parameters: Optional[list[str]] = None, body: Optional[str] = None, executor: Optional[ProcedureExecutor] = None):
        if isinstance(name, ProcedureDescriptor):
            self.descriptor = name
        else:
            self.descriptor = ProcedureDescriptor(name, parameters or [], body or "")
        
        self.name = self.descriptor.name
        self.parameters = self.descriptor.parameters
        self.body = self.descriptor.body
        self.executor = executor or ProcedureExecutor()

class StoredProcedureManager:
    def __init__(self):
        # database_name -> dict of procedures (proc_name -> StoredProcedure)
        self.procedures: dict[str, dict[str, StoredProcedure]] = {}

    def create_procedure(self, database_name: str, proc_name: str, parameters: list[str], body: str) -> StoredProcedure:
        if database_name not in self.procedures:
            self.procedures[database_name] = {}
        if proc_name in self.procedures[database_name]:
            raise ValueError(f"Procedure {proc_name} already exists in database {database_name}")
        
        # Build ProcedureDescriptor
        descriptor = ProcedureDescriptor(proc_name, parameters, body)
        proc = StoredProcedure(descriptor)
        
        self.procedures[database_name][proc_name] = proc
        return proc

    def drop_procedure(self, database_name: str, proc_name: str) -> None:
        if database_name in self.procedures and proc_name in self.procedures[database_name]:
            del self.procedures[database_name][proc_name]

    def get_procedure(self, database_name: str, proc_name: str) -> StoredProcedure:
        if database_name not in self.procedures or proc_name not in self.procedures[database_name]:
            raise ValueError(f"Procedure {proc_name} not found in database {database_name}")
        return self.procedures[database_name][proc_name]
