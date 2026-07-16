from dbms.database_object.database_manager import DatabaseManager


def test_database_manager_can_be_created():
    assert isinstance(DatabaseManager(), DatabaseManager)
