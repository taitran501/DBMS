from typing import Union, Optional

class RelationshipDescriptor:
    def __init__(self, name: str, source_table: str, target_table: str, relationship_type: str):
        self.name = name
        self.source_table = source_table
        self.target_table = target_table
        self.relationship_type = relationship_type

class ReferentialActionPolicy:
    def __init__(self, on_delete: str = "NO_ACTION", on_update: str = "NO_ACTION"):
        self.on_delete = on_delete
        self.on_update = on_update

class Relationship:
    def __init__(self, name: Union[str, RelationshipDescriptor], source_table: Optional[str] = None, target_table: Optional[str] = None, relationship_type: Optional[str] = None, policy: Optional[ReferentialActionPolicy] = None):
        if isinstance(name, RelationshipDescriptor):
            self.descriptor = name
        else:
            self.descriptor = RelationshipDescriptor(name, source_table or "", target_table or "", relationship_type or "")
        
        self.name = self.descriptor.name
        self.source_table = self.descriptor.source_table
        self.target_table = self.descriptor.target_table
        self.relationship_type = self.descriptor.relationship_type
        self.policy = policy or ReferentialActionPolicy()

class RelationshipManager:
    def __init__(self):
        self.relationships: dict[str, Relationship] = {}

    def create_relationship(self, relationship: Relationship) -> None:
        if relationship.name in self.relationships:
            raise ValueError(f"Relationship {relationship.name} already exists")
        self.relationships[relationship.name] = relationship

    def drop_relationship(self, name: str) -> None:
        if name in self.relationships:
            del self.relationships[name]

    def get_relationship(self, name: str) -> Relationship:
        if name not in self.relationships:
            raise ValueError(f"Relationship {name} not found")
        return self.relationships[name]
