from dbms.security_access_control.permission import Permission


def test_permission_can_be_created():
    p = Permission("table1", "read")
    assert p.resource == "table1"
    assert p.action == "read"


def test_matches():
    p = Permission("table1", "read")
    assert p.matches("table1", "read") is True
    assert p.matches("table1", "write") is False
