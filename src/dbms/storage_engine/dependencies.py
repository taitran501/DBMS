from typing import Protocol, runtime_checkable

from dbms.storage_engine.page import Page


@runtime_checkable
class PageStoreProtocol(Protocol):
    def load_page(self, page_id: int) -> Page | None: ...

    def write_page(self, page: Page) -> bool: ...
