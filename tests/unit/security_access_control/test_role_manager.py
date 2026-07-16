from dbms.security_access_control.role_manager import RoleManager


def test_role_manager_can_be_created():
    assert isinstance(RoleManager(), RoleManager)
