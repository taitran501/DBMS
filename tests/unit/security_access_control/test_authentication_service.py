from dbms.security_access_control.authentication_service import AuthenticationService


def test_authentication_service_can_be_created():
    assert isinstance(AuthenticationService(), AuthenticationService)
