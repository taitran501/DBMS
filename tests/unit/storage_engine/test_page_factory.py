import pytest

from dbms.storage_engine.page import Page
from dbms.storage_engine.page_factory import (
    DataPage,
    DataPageFactory,
    IndexPage,
    IndexPageFactory,
    PageFactory,
)


def test_data_page_factory_creates_data_page():
    # Arrange
    factory: PageFactory = DataPageFactory()

    # Act
    page = factory.create_page(page_id=1, data=b"header_info")

    # Assert
    assert isinstance(page, DataPage)
    assert isinstance(page, Page)
    assert page.page_id == 1
    assert page.data == b"header_info"
    assert page.page_type == "DATA"


def test_index_page_factory_creates_index_page():
    # Arrange
    factory: PageFactory = IndexPageFactory()

    # Act
    page = factory.create_page(page_id=10, data=b"btree_root")

    # Assert
    assert isinstance(page, IndexPage)
    assert isinstance(page, Page)
    assert page.page_id == 10
    assert page.data == b"btree_root"
    assert page.page_type == "INDEX"


def test_factory_created_pages_support_tuple_operations():
    # Arrange
    factory = DataPageFactory()
    page = factory.create_page(page_id=2)

    # Act
    slot_id = page.insert_tuple(b"record_data")
    read_payload = page.read_tuple(slot_id)

    # Assert
    assert slot_id == 0
    assert read_payload == b"record_data"


def test_data_page_serialization_and_deserialization():
    # Arrange
    factory = DataPageFactory()
    original_page = factory.create_page(page_id=5, data=b"meta")
    slot_id = original_page.insert_tuple(b"sample_payload")

    # Act
    serialized_bytes = original_page.serialize()
    restored_page = DataPage.deserialize(serialized_bytes)

    # Assert
    assert restored_page.page_id == 5
    assert restored_page.data == b"meta"
    assert restored_page.read_tuple(slot_id) == b"sample_payload"


def test_index_page_serialization_and_deserialization():
    # Arrange
    factory = IndexPageFactory()
    original_page = factory.create_page(page_id=42, data=b"root_node")
    slot_id = original_page.insert_tuple(b"key:100->row_1")

    # Act
    serialized_bytes = original_page.serialize()
    restored_page = IndexPage.deserialize(serialized_bytes)

    # Assert
    assert restored_page.page_id == 42
    assert restored_page.data == b"root_node"
    assert restored_page.read_tuple(slot_id) == b"key:100->row_1"
