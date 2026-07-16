from dbms.database_object.view_manager import ViewManager


def test_view_manager_can_be_created():
    assert isinstance(ViewManager(), ViewManager)
