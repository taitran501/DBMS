import pytest

from dbms.storage_engine.exceptions import StoragePathError
from dbms.storage_engine.file_manager import FileManager
from dbms.storage_engine.page import Page


def test_file_manager_can_be_created(tmp_path):
    """Ensure FileManager initializes with a given root path and proper interface methods."""
    # Arrange
    root_path = str(tmp_path)

    # Act
    manager = FileManager(root_path)

    # Assert
    assert manager.root_path == root_path
    assert callable(manager.create_file)
    assert callable(manager.read)
    assert callable(manager.write)


def test_create_file(tmp_path):
    """Ensure FileManager can create a physical data file under its root path."""
    # Arrange
    manager = FileManager(str(tmp_path))

    # Act
    result = manager.create_file("db.dat")

    # Assert
    assert result is True
    assert (tmp_path / "db.dat").exists()


def test_read_file_bytes(tmp_path):
    """Ensure FileManager can read binary byte slices from a specific offset and length."""
    # Arrange: Write sample data to disk
    manager = FileManager(str(tmp_path))
    path = tmp_path / "db.dat"
    path.write_bytes(b"page_data")

    # Act: Read data bytes back via FileManager
    result = manager.read("db.dat", offset=0, length=9)

    # Assert
    assert result == b"page_data"


def test_write(tmp_path):
    """Ensure FileManager can write binary byte data to a file at specified offset."""
    # Arrange: Create target file
    manager = FileManager(str(tmp_path))
    manager.create_file("db.dat")

    # Act: Write byte data to file
    result = manager.write("db.dat", offset=0, data=b"new_data")

    # Assert
    assert result is True
    assert (tmp_path / "db.dat").read_bytes() == b"new_data"


def test_create_file_rejects_path_outside_root(tmp_path):
    """Ensure directory traversal attacks (e.g. '../outside.dat') are blocked

    and raise StoragePathError to keep operations within the root directory.
    """
    # Arrange: Setup file manager and construct a relative path outside root
    manager = FileManager(str(tmp_path))
    outside_name = f"{tmp_path.name}-outside.dat"

    # Act & Assert: Attempting to create file outside root path must raise StoragePathError
    with pytest.raises(StoragePathError):
        manager.create_file(f"../{outside_name}")

    assert not (tmp_path.parent / outside_name).exists()


def test_write_and_load_page_through_page_store_adapter(tmp_path):
    manager = FileManager(str(tmp_path))
    page = Page(5, b"header")
    page.write_tuple(2, b"customer-row")

    assert manager.write_page(page) is True
    restored_page = manager.load_page(5)

    assert restored_page is not None
    assert restored_page.page_id == 5
    assert restored_page.data == b"header"
    assert restored_page.read_tuple(2) == b"customer-row"


def test_load_missing_page_returns_none(tmp_path):
    manager = FileManager(str(tmp_path))

    assert manager.load_page(99) is None
