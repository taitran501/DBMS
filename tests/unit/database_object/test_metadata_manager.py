from dbms.database_object.metadata_manager import MetadataManager


def test_metadata_manager_can_be_created():
    assert isinstance(MetadataManager(), MetadataManager)
