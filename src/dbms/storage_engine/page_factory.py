from abc import ABC, abstractmethod

from dbms.storage_engine.page import Page


class DataPage(Page):
    """Specialized page for storing serialized tuple records."""

    page_type: str = "DATA"


class IndexPage(Page):
    """Specialized page for storing index keys and child node pointers."""

    page_type: str = "INDEX"


class PageFactory(ABC):
    """Abstract creator class defining the factory method for Page allocation."""

    @abstractmethod
    def create_page(self, page_id: int, data: bytes = b"") -> Page:
        """Create and return a concrete Page instance."""
        pass


class DataPageFactory(PageFactory):
    """Concrete factory for creating DataPage instances."""

    def create_page(self, page_id: int, data: bytes = b"") -> DataPage:
        return DataPage(page_id=page_id, data=data)


class IndexPageFactory(PageFactory):
    """Concrete factory for creating IndexPage instances."""

    def create_page(self, page_id: int, data: bytes = b"") -> IndexPage:
        return IndexPage(page_id=page_id, data=data)
