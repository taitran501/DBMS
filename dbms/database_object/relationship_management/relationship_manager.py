from dataclasses import dataclass

@dataclass(frozen=True)
class RelationshipDescriptor:
    name: str
    source_table: str
    target_table: str
    relationship_type: str
    source_columns: tuple[str, ...] = ()
    target_columns: tuple[str, ...] = ()

@dataclass(frozen=True)
class ReferentialActionPolicy:
    on_delete: str = "NO_ACTION"
    on_update: str = "NO_ACTION"

class Relationship:
    def __init__(self, name, source_table=None, target_table=None, relationship_type=None, policy=None, source_columns=(), target_columns=()):
        self.descriptor = name if isinstance(name, RelationshipDescriptor) else RelationshipDescriptor(name, source_table or "", target_table or "", relationship_type or "", tuple(source_columns), tuple(target_columns))
        self.name = self.descriptor.name; self.source_table = self.descriptor.source_table; self.target_table = self.descriptor.target_table
        self.relationship_type = self.descriptor.relationship_type; self.policy = policy or ReferentialActionPolicy()

class RelationshipManager:
    def __init__(self): self.relationships = {}
    def create_relationship(self, relationship):
        if relationship.name in self.relationships: raise ValueError(f"Relationship {relationship.name} already exists")
        self.relationships[relationship.name] = relationship
    def drop_relationship(self, name): self.relationships.pop(name, None)
    def get_relationship(self, name):
        if name not in self.relationships: raise ValueError(f"Relationship {name} not found")
        return self.relationships[name]
    def validate_row(self, table_name, row, table_manager):
        for rel in self.relationships.values():
            d = rel.descriptor
            if d.source_table != table_name or not d.source_columns: continue
            values = tuple(row.get(c) for c in d.source_columns)
            if any(v is None for v in values): continue
            target = table_manager.find_table(d.target_table)
            if not any(tuple(item.get(c) for c in d.target_columns) == values for item in target.rows.values()):
                raise ValueError(f"Relationship {rel.name} rejected row")
    def rename_table(self, table_name, new_table_name):
        for relationship in self.relationships.values():
            descriptor = relationship.descriptor
            source = new_table_name if descriptor.source_table == table_name else descriptor.source_table
            target = new_table_name if descriptor.target_table == table_name else descriptor.target_table
            relationship.descriptor = RelationshipDescriptor(descriptor.name, source, target, descriptor.relationship_type, descriptor.source_columns, descriptor.target_columns)
            relationship.source_table, relationship.target_table = source, target
    def rename_column(self, table_name, column_name, new_name):
        for relationship in self.relationships.values():
            descriptor = relationship.descriptor
            source_columns = tuple(new_name if descriptor.source_table == table_name and column == column_name else column for column in descriptor.source_columns)
            target_columns = tuple(new_name if descriptor.target_table == table_name and column == column_name else column for column in descriptor.target_columns)
            relationship.descriptor = RelationshipDescriptor(descriptor.name, descriptor.source_table, descriptor.target_table, descriptor.relationship_type, source_columns, target_columns)
