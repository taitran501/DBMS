from dbms.storage_engine.file_manager import FileManager


def test_file_manager_can_be_created(tmp_path):
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
    # Arrange
    manager = FileManager(str(tmp_path))

    # Act
    result = manager.create_file("db.dat")

    # Assert
    assert result is True
    assert (tmp_path / "db.dat").exists()


def test_read_file_bytes(tmp_path):
    # Arrange
    manager = FileManager(str(tmp_path))
    path = tmp_path / "db.dat"
    path.write_bytes(b"page_data")

    # Act
    result = manager.read("db.dat", offset=0, length=9)

    # Assert
    assert result == b"page_data"


def test_write(tmp_path):
    # Arrange
    manager = FileManager(str(tmp_path))
    manager.create_file("db.dat")

    # Act
    result = manager.write("db.dat", offset=0, data=b"new_data")

    # Assert
    assert result is True
    assert (tmp_path / "db.dat").read_bytes() == b"new_data"
