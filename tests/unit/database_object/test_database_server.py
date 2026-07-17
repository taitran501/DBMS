from dbms.database_object.database_server import DatabaseServer


def test_database_server_can_be_created():
    server = DatabaseServer("srv1", "1.0", "stopped")

    assert server.server_id == "srv1"
    assert server.version == "1.0"
    assert server.status == "stopped"
    assert callable(server.start)
    assert callable(server.stop)
    assert callable(server.restart)


def test_start_server():
    pass


def test_stop_server():
    pass


def test_restart_server():
    pass
