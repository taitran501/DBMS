from threading import RLock

from dbms.storage_engine.buffer_replacement_strategy import (
    BufferReplacementStrategy,
    FifoReplacementStrategy,
)
from dbms.storage_engine.dependencies import PageStoreProtocol
from dbms.storage_engine.exceptions import BufferPoolFullError
from dbms.storage_engine.page import Page


_UNSET = object()


class BufferPool:
    """Cache proxy that controls page access to a PageStoreProtocol."""

    _instance: "BufferPool | None" = None
    _instance_lock = RLock()

    def __new__(
        cls,
        capacity: int,
        page_store: PageStoreProtocol | None = None,
        replacement_strategy: BufferReplacementStrategy | None = None,
    ) -> "BufferPool":
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._is_initialized = False
            return cls._instance

    def __init__(
        self,
        capacity: int,
        page_store: PageStoreProtocol | None = None,
        replacement_strategy: BufferReplacementStrategy | None = None,
    ) -> None:
        with type(self)._instance_lock:
            if self._is_initialized:
                self._validate_configuration(
                    capacity,
                    page_store,
                    replacement_strategy,
                )
                return
            if capacity <= 0:
                type(self)._instance = None
                raise ValueError("Buffer pool capacity must be positive")
            self.capacity = capacity
            self.page_store = page_store
            self.replacement_strategy = replacement_strategy or FifoReplacementStrategy()
            self.pages: dict[int, Page] = {}
            self.pin_counts: dict[int, int] = {}
            self.dirty_page_ids: set[int] = set()
            self._is_initialized = True

    @classmethod
    def get_instance(
        cls,
        capacity: int | None = None,
        page_store: PageStoreProtocol | None | object = _UNSET,
        replacement_strategy: BufferReplacementStrategy | None | object = _UNSET,
    ) -> "BufferPool":
        """Get or create the singleton BufferPool instance."""
        with cls._instance_lock:
            if cls._instance is None:
                return cls(
                    capacity=capacity if capacity is not None else 10,
                    page_store=None if page_store is _UNSET else page_store,
                    replacement_strategy=(
                        None if replacement_strategy is _UNSET else replacement_strategy
                    ),
                )

            cls._instance._validate_requested_configuration(
                capacity,
                page_store,
                replacement_strategy,
            )
            return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (primarily for testing isolation)."""
        with cls._instance_lock:
            cls._instance = None

    def pin_page(self, page_id: int) -> Page | None:
        page = self.get_cached_page(page_id)
        if page is None:
            if self.page_store is None:
                return None
            page = self.page_store.load_page(page_id)
            if page is None or not self.cache_page(page):
                return None

        self.pin_counts[page_id] += 1
        self.replacement_strategy.record_access(page_id)
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
        self.replacement_strategy.record_page(page.page_id)
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
        self.replacement_strategy.remove_page(page_id)
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
        candidates = [
            page_id
            for page_id in self.pages
            if self.pin_counts.get(page_id, 0) == 0
        ]
        return self.replacement_strategy.select_victim(candidates)

    def _validate_configuration(
        self,
        capacity: int,
        page_store: PageStoreProtocol | None,
        replacement_strategy: BufferReplacementStrategy | None,
    ) -> None:
        if (
            capacity != self.capacity
            or page_store is not self.page_store
            or (
                replacement_strategy is not None
                and replacement_strategy is not self.replacement_strategy
            )
        ):
            raise ValueError("BufferPool singleton is already configured differently")

    def _validate_requested_configuration(
        self,
        capacity: int | None,
        page_store: PageStoreProtocol | None | object,
        replacement_strategy: BufferReplacementStrategy | None | object,
    ) -> None:
        if capacity is not None and capacity != self.capacity:
            raise ValueError("BufferPool singleton is already configured differently")
        if page_store is not _UNSET and page_store is not self.page_store:
            raise ValueError("BufferPool singleton is already configured differently")
        if (
            replacement_strategy is not _UNSET
            and replacement_strategy is not self.replacement_strategy
        ):
            raise ValueError("BufferPool singleton is already configured differently")
