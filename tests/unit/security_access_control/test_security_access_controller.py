from dbms.security_access_control.security_access_controller import SecurityAccessController


def test_security_access_controller_can_be_created():
    assert isinstance(SecurityAccessController(), SecurityAccessController)
