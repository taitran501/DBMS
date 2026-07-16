from dbms.security_access_control.authorization_service import AuthorizationService

def test_grant_permission():
    pass

def test_revoke_permission():
    pass

def test_check_user_permission():
    pass

def test_check_role_permission():
    pass

def test_inherit_permission():
    pass

def test_deny_missing_permission():
    pass

def test_isolate_object_permission():
    pass

def test_authorization_service_can_be_created():
    assert isinstance(AuthorizationService(), AuthorizationService)
