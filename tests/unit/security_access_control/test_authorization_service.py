from dbms.security_access_control.authorization_service import AuthorizationService


def test_authorization_service_can_be_created():
    assert isinstance(AuthorizationService(), AuthorizationService)
