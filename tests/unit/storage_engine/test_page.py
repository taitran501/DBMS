from dbms.storage_engine.page import Page


def test_page_can_be_created():
    page = Page(1, b"data")
    assert page.page_id == 1
    assert page.data == b"data"
    assert page.read() == b""
    assert page.write(b"new data") is True


def test_read_tuple():
    page = Page(1, b"data")
    assert page.read_tuple() is None


def test_write_tuple():
    page = Page(1, b"data")
    assert page.write_tuple(object()) is True


