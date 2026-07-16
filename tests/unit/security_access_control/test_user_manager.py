from dbms.security_access_control.user_manager import UserManager


def test_user_manager_can_be_created():
    assert isinstance(UserManager(), UserManager)
