from dbms.database_object.database_object_manager import DatabaseObjectManager


def test_database_object_manager_can_be_created():
    assert isinstance(DatabaseObjectManager(), DatabaseObjectManager)
