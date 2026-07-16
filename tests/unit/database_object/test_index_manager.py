from dbms.database_object.index_manager import IndexManager


def test_index_manager_can_be_created():
    assert isinstance(IndexManager(), IndexManager)
