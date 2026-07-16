from dbms.database_object.column_manager import ColumnManager


def test_column_manager_can_be_created():
    assert isinstance(ColumnManager(), ColumnManager)
