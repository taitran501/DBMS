from dbms.storage_engine.page import Page


def test_initialize_page():
    pass


def test_page_stores_attributes_and_returns_placeholders():
    page = Page(1, b"data")

    assert page.page_id == 1
    assert page.data == b"data"
    assert page.read() == b""
    assert page.write(b"new data") is True

