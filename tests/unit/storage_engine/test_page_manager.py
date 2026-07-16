from dbms.storage_engine.page_manager import PageManager


def test_page_manager_can_be_created():
    assert isinstance(PageManager(), PageManager)
