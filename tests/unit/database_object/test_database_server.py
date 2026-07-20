import pytest

from dbms.database_object.database_server import DatabaseServer


def test_database_server_can_be_created():
    # Arrange
    server = DatabaseServer("srv1", "1.0", "stopped")

    # Assert
    assert server.server_id == "srv1"
    assert server.version == "1.0"
    assert server.status == "stopped"
    assert callable(server.start)
    assert callable(server.stop)
    assert callable(server.restart)


def test_start():
    # Arrange
    server = DatabaseServer("srv1", "1.0", "stopped")

    # Act
    result = server.start()

    # Assert
    assert result is True
    assert server.status == "running"


def test_stop():
    # Arrange
    server = DatabaseServer("srv1", "1.0", "running")

    # Act
    result = server.stop()

    # Assert
    assert result is True
    assert server.status == "stopped"


def test_restart():
    # Arrange
    server = DatabaseServer("srv1", "1.0", "running")

    # Act
    result = server.restart()

    # Assert
    assert result is True
    assert server.status == "running"


def test_start_already_running_server_raises_exception():
    # Arrange: Server is already running
    server = DatabaseServer("srv1", "1.0", "running")

    # Act & Assert: Starting an already running server should raise RuntimeError
    with pytest.raises(RuntimeError):
        server.start()


def test_stop_already_stopped_server_raises_exception():
    # Arrange: Server is already stopped
    server = DatabaseServer("srv1", "1.0", "stopped")

    # Act & Assert: Stopping an already stopped server should raise RuntimeError
    with pytest.raises(RuntimeError):
        server.stop()
