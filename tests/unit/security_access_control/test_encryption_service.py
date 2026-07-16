from dbms.security_access_control.encryption_service import EncryptionService


def test_encryption_service_can_be_created():
    assert isinstance(EncryptionService(), EncryptionService)
