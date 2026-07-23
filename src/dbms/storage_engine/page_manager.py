from dbms.storage_engine.page import Page


class PageManager:
    """Owns the in-memory pages used by the RecordManager."""

    def __init__(self) -> None:
        self.pages: dict[int, Page] = {}
        self._available_page_ids: list[int] = []
        self._next_page_id = 1

    def allocate_page(self) -> int:
        if self._available_page_ids:
            page_id = self._available_page_ids.pop(0)
        else:
            page_id = self._next_page_id
            self._next_page_id += 1

        self.pages[page_id] = Page(page_id)
        return page_id

    def get_page(self, page_id: int) -> Page | None:
        return self.pages.get(page_id)

    def release_page(self, page_id: int, *, deallocate: bool = False) -> bool:
        if page_id not in self.pages:
            return False

        if deallocate:
            del self.pages[page_id]
            self._available_page_ids.append(page_id)
            self._available_page_ids.sort()
        return True

    def get_page_with_free_space(self, required_bytes: int) -> Page:
        for page in self.pages.values():
            if page.free_space >= required_bytes:
                return page

        if required_bytes > Page.PAGE_SIZE:
            raise ValueError("Tuple size exceeds available page space")

        page_id = self.allocate_page()
        return self.pages[page_id]

    def track_page_free_space(self, page_id: int) -> int:
        page = self.get_page(page_id)
        if page is None:
            return 0
        return page.free_space
