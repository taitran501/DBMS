from dbms.storage_engine.page import Page
from dbms.storage_engine.dependencies import PageStoreProtocol
from dbms.storage_engine.exceptions import BufferPoolFullError


class BufferPool:
    """Cache proxy that controls page access to a PageStoreProtocol."""

    def __init__(self, capacity: int, page_store: PageStoreProtocol | None = None) -> None:
        if capacity <= 0:
            raise ValueError("Buffer pool capacity must be positive")
        self.capacity = capacity
        self.page_store = page_store
        self.pages: dict[int, Page] = {}
        self.pin_counts: dict[int, int] = {}
        self.dirty_page_ids: set[int] = set()

    def pin_page(self, page_id: int) -> Page | None:
        page = self.get_cached_page(page_id)
        if page is None:
            if self.page_store is None:
                return None
            page = self.page_store.load_page(page_id)
            if page is None or not self.cache_page(page):
                return None

        self.pin_counts[page_id] += 1
        return page

    def unpin_page(self, page_id: int) -> bool:
        pin_count = self.pin_counts.get(page_id)
        if pin_count is None or pin_count == 0:
            return False
        self.pin_counts[page_id] = pin_count - 1
        return True

    def cache_page(self, page: Page) -> bool:
        if page.page_id not in self.pages and len(self.pages) >= self.capacity:
            if self._select_victim() is None:
                raise BufferPoolFullError("All cached pages are pinned")
            if not self.evict_page():
                return False

        self.pages[page.page_id] = page
        self.pin_counts.setdefault(page.page_id, 0)
        return True

    def get_cached_page(self, page_id: int) -> Page | None:
        return self.pages.get(page_id)

    def evict_page(self) -> bool:
        page_id = self._select_victim()
        if page_id is None:
            return False
        if page_id in self.dirty_page_ids and not self.flush_page(page_id):
            return False

        del self.pages[page_id]
        del self.pin_counts[page_id]
        self.dirty_page_ids.discard(page_id)
        return True

    def mark_dirty(self, page_id: int) -> bool:
        if page_id not in self.pages:
            return False
        self.dirty_page_ids.add(page_id)
        return True

    def flush_page(self, page_id: int) -> bool:
        page = self.get_cached_page(page_id)
        if page is None:
            return False
        if page_id not in self.dirty_page_ids:
            return True
        if self.page_store is None or not self.page_store.write_page(page):
            return False

        self.dirty_page_ids.remove(page_id)
        return True

    def flush_all_pages(self) -> bool:
        return all(self.flush_page(page_id) for page_id in list(self.dirty_page_ids))

    def _select_victim(self) -> int | None:
        return next(
            (
                page_id
                for page_id in self.pages
                if self.pin_counts.get(page_id, 0) == 0
            ),
            None,
        )
