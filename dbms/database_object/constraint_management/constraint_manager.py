from typing import Union, Optional

class ConstraintDescriptor:
    def __init__(self, name: str, constraint_type: str, columns: list[str]):
        self.name = name
        self.constraint_type = constraint_type  # e.g., PRIMARY_KEY, UNIQUE, CHECK
        self.columns = columns

class ConstraintEnforcer:
    def __init__(self):
        pass

    def validate(self, descriptor: ConstraintDescriptor, value_dict: dict) -> bool:
        # Placeholder validation logic
        return True

class Constraint:
    def __init__(self, name: Union[str, ConstraintDescriptor], constraint_type: Optional[str] = None, columns: Optional[list[str]] = None, enforcer: Optional[ConstraintEnforcer] = None):
        if isinstance(name, ConstraintDescriptor):
            self.descriptor = name
        else:
            self.descriptor = ConstraintDescriptor(name, constraint_type or "", columns or [])
        
        self.name = self.descriptor.name
        self.constraint_type = self.descriptor.constraint_type
        self.columns = self.descriptor.columns
        self.enforcer = enforcer or ConstraintEnforcer()

class ConstraintManager:
    def __init__(self):
        # table_name -> list of Constraint objects
        self.constraints: dict[str, list[Constraint]] = {}

    def create_constraint(self, table_name: str, constraint: Constraint) -> None:
        if table_name not in self.constraints:
            self.constraints[table_name] = []
        if any(c.name == constraint.name for c in self.constraints[table_name]):
            raise ValueError(f"Constraint {constraint.name} already exists in table {table_name}")
        self.constraints[table_name].append(constraint)

    def drop_constraint(self, table_name: str, constraint_name: str) -> None:
        if table_name in self.constraints:
            self.constraints[table_name] = [c for c in self.constraints[table_name] if c.name != constraint_name]

    def get_constraint(self, table_name: str, constraint_name: str) -> Constraint:
        if table_name in self.constraints:
            for c in self.constraints[table_name]:
                if c.name == constraint_name:
                    return c
        raise ValueError(f"Constraint {constraint_name} not found in table {table_name}")

    def validate_row(self, table_name: str, values: dict) -> None:
        for constraint in self.constraints.get(table_name, []):
            if not constraint.enforcer.validate(constraint.descriptor, values):
                raise ValueError(f"Constraint {constraint.name} rejected row")
