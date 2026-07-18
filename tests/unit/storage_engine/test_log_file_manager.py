import pytest

from dbms.storage_engine.log_file_manager import LogFileManager


def test_log_file_manager_can_be_created():
    # Arrange / Act
    manager = LogFileManager()

    # Assert
    assert callable(manager.append_log_entry)
    assert callable(manager.read_log_entry)
    assert callable(manager.read_log_range)
    assert callable(manager.flush_log)
    assert callable(manager.truncate_log)


def test_append_log_entry():
    # Arrange
    manager = LogFileManager()

    # Act
    lsn = manager.append_log_entry(b"log_data")

    # Assert
    assert lsn == 1


def test_read_log_entry():
    # Arrange
    manager = LogFileManager()
    lsn = manager.append_log_entry(b"log_data")

    # Act
    result = manager.read_log_entry(lsn)

    # Assert
    assert result == b"log_data"


def test_read_log_range():
    # Arrange
    manager = LogFileManager()
    first_lsn = manager.append_log_entry(b"entry1")
    manager.append_log_entry(b"entry2")

    # Act
    result = manager.read_log_range(first_lsn, first_lsn + 1)

    # Assert
    assert result == [b"entry1", b"entry2"]


def test_detect_corrupted_entry():
    # Arrange
    manager = LogFileManager()
    lsn = manager.append_log_entry(b"log_data")
    manager.entries[lsn] = (b"log_data", "invalid-checksum")

    # Act / Assert
    with pytest.raises(Exception, match="checksum"):
        manager.read_log_entry(lsn)


def test_flush_log():
    # Arrange
    manager = LogFileManager()
    manager.append_log_entry(b"log_data")

    # Act
    result = manager.flush_log()

    # Assert
    assert result is True


def test_truncate_log():
    # Arrange
    manager = LogFileManager()
    manager.append_log_entry(b"entry1")
    second_lsn = manager.append_log_entry(b"entry2")

    # Act
    result = manager.truncate_log(second_lsn)

    # Assert
    assert result is True
    assert manager.read_log_entry(1) is None
    assert manager.read_log_entry(second_lsn) == b"entry2"


def test_assign_sequence_number():
    # Arrange
    manager = LogFileManager()

    # Act
    first_lsn = manager.append_log_entry(b"first")
    second_lsn = manager.append_log_entry(b"second")

    # Assert
    assert first_lsn == 1
    assert second_lsn == 2
