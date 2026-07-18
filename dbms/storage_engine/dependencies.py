from typing import Protocol, runtime_checkable


@runtime_checkable
class PageStoreProtocol(Protocol):
    def load_page(self, page_id: int) -> object | None: ...

    def write_page(self, page: object) -> bool: ...
