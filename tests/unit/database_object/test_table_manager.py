from dbms.database_object.table_manager import TableManager


def test_table_manager_can_be_created():
    assert isinstance(TableManager(), TableManager)
