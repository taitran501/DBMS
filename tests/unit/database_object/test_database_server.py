from dbms.database_object.database_server import DatabaseServer


def test_database_server_can_be_created():
    server = DatabaseServer("srv1", "1.0", "stopped")

    assert server.server_id == "srv1"
    assert server.version == "1.0"
    assert server.status == "stopped"
    assert callable(server.start)
    assert callable(server.stop)
    assert callable(server.restart)


def test_start():
    server = DatabaseServer("srv1", "1.0", "stopped")

    result = server.start()

    assert result is True
    assert server.status == "running"


def test_stop():
    server = DatabaseServer("srv1", "1.0", "running")

    result = server.stop()

    assert result is True
    assert server.status == "stopped"


def test_restart():
    server = DatabaseServer("srv1", "1.0", "running")

    result = server.restart()

    assert result is True
    assert server.status == "running"
