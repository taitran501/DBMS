from dataclasses import dataclass
from typing import Callable, Optional
from dbms.errors import ConstraintViolationError

@dataclass(frozen=True)
class ConstraintDescriptor:
    name: str
    constraint_type: str
    columns: tuple[str, ...]
    predicate: Optional[Callable[[dict], bool]] = None

class ConstraintEnforcer:
    def validate(self, descriptor, row, existing_rows=()):
        kind = descriptor.constraint_type.upper(); values = tuple(row.get(c) for c in descriptor.columns)
        if kind in {"NOT_NULL", "PRIMARY_KEY"} and any(v is None for v in values): return False
        if kind in {"PRIMARY_KEY", "UNIQUE"} and not (kind == "UNIQUE" and any(v is None for v in values)):
            if any(tuple(other.get(c) for c in descriptor.columns) == values for other in existing_rows): return False
        if kind == "CHECK" and descriptor.predicate is not None: return bool(descriptor.predicate(row))
        return True

class Constraint:
    def __init__(self, name, constraint_type=None, columns=None, enforcer=None, predicate=None):
        self.descriptor = name if isinstance(name, ConstraintDescriptor) else ConstraintDescriptor(name, constraint_type or "", tuple(columns or ()), predicate)
        self.name = self.descriptor.name; self.constraint_type = self.descriptor.constraint_type; self.columns = list(self.descriptor.columns)
        self.enforcer = enforcer or ConstraintEnforcer()

class ConstraintManager:
    def __init__(self): self.constraints = {}
    def create_constraint(self, table_name, constraint):
        items = self.constraints.setdefault(table_name, [])
        if any(c.name == constraint.name for c in items): raise ValueError(f"Constraint {constraint.name} already exists in table {table_name}")
        items.append(constraint)
    def drop_constraint(self, table_name, constraint_name):
        if table_name in self.constraints: self.constraints[table_name] = [c for c in self.constraints[table_name] if c.name != constraint_name]
    def get_constraint(self, table_name, constraint_name):
        for item in self.constraints.get(table_name, []):
            if item.name == constraint_name: return item
        raise ValueError(f"Constraint {constraint_name} not found in table {table_name}")
    def validate_row(self, table_name, values, existing_rows=()):
        for constraint in self.constraints.get(table_name, []):
            try: valid = constraint.enforcer.validate(constraint.descriptor, values, existing_rows)
            except TypeError: valid = constraint.enforcer.validate(constraint.descriptor, values)
            if not valid:
                raise ConstraintViolationError(f"Constraint {constraint.name} rejected row")
