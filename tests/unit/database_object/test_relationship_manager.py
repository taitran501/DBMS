from dbms.database_object.relationship_manager import RelationshipManager


def test_relationship_manager_can_be_created():
    assert isinstance(RelationshipManager(), RelationshipManager)
