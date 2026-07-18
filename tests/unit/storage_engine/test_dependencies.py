from dbms.storage_engine.dependencies import PageStoreProtocol
from dbms.storage_engine.page import Page


def test_page_store_stub_matches_protocol():
    # Arrange
    class PageStoreStub:
        def load_page(self, page_id: int) -> Page | None:
            return None

        def write_page(self, page: Page) -> bool:
            return True

    # Assert
    assert isinstance(PageStoreStub(), PageStoreProtocol)
