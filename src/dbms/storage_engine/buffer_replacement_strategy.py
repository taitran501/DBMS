from abc import ABC, abstractmethod
from collections import OrderedDict
from collections.abc import Collection


class BufferReplacementStrategy(ABC):
    """Selects an evictable page without owning buffer-pool state."""

    def record_page(self, page_id: int) -> None:
        """Record that a page entered the buffer pool."""

    def record_access(self, page_id: int) -> None:
        """Record that a page was pinned from the buffer pool."""

    def remove_page(self, page_id: int) -> None:
        """Stop tracking a page that left the buffer pool."""

    @abstractmethod
    def select_victim(self, candidate_page_ids: Collection[int]) -> int | None:
        """Return one unpinned page id, or None when no candidate exists."""


class FifoReplacementStrategy(BufferReplacementStrategy):
    """Evicts the earliest cached unpinned page."""

    def __init__(self) -> None:
        self._page_order: list[int] = []

    def record_page(self, page_id: int) -> None:
        if page_id not in self._page_order:
            self._page_order.append(page_id)

    def remove_page(self, page_id: int) -> None:
        if page_id in self._page_order:
            self._page_order.remove(page_id)

    def select_victim(self, candidate_page_ids: Collection[int]) -> int | None:
        return next(
            (page_id for page_id in self._page_order if page_id in candidate_page_ids),
            None,
        )


class LruReplacementStrategy(BufferReplacementStrategy):
    """Evicts the least recently pinned unpinned page."""

    def __init__(self) -> None:
        self._page_order: OrderedDict[int, None] = OrderedDict()

    def record_page(self, page_id: int) -> None:
        self._page_order[page_id] = None

    def record_access(self, page_id: int) -> None:
        if page_id in self._page_order:
            self._page_order.move_to_end(page_id)

    def remove_page(self, page_id: int) -> None:
        self._page_order.pop(page_id, None)

    def select_victim(self, candidate_page_ids: Collection[int]) -> int | None:
        return next(
            (page_id for page_id in self._page_order if page_id in candidate_page_ids),
            None,
        )
