from dbms.storage_engine.page import Page


def test_page_can_be_created():
    # Arrange / Act
    page = Page(1, b"initial_data")

    # Assert
    assert page.page_id == 1
    assert page.data == b"initial_data"
    assert callable(page.read_tuple)
    assert callable(page.write_tuple)


def test_read_tuple():
    # Arrange
    page = Page(1, b"")
    page.write_tuple(10, b"tuple_data")

    # Act
    result = page.read_tuple(10)

    # Assert
    assert result == b"tuple_data"


def test_write_tuple():
    # Arrange
    page = Page(1, b"")

    # Act
    result = page.write_tuple(10, b"tuple_data")

    # Assert
    assert result is True
    assert page.read_tuple(10) == b"tuple_data"
