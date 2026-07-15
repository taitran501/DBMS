class DBMSError(Exception):
    pass

class ColumnNotFoundError(DBMSError):
    def __init__(self, name: str):
        super().__init__(f"Column '{name}' not found.")

class TableAlreadyExistsError(DBMSError):
    def __init__(self, name: str):
        super().__init__(f"Table '{name}' already exists.")

class TableNotFoundError(DBMSError):
    def __init__(self, name: str):
        super().__init__(f"Table '{name}' not found.")

class ObjectNotFoundError(DBMSError): pass
class DependencyExistsError(DBMSError): pass
class ConstraintViolationError(DBMSError, ValueError): pass
class RowNotFoundError(DBMSError): pass
class ProcedureNotExecutableError(DBMSError): pass
class TriggerNotExecutableError(DBMSError): pass
