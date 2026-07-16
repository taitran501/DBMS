from dbms.security_access_control.audit_logger import AuditLogger


def test_audit_logger_can_be_created():
    assert isinstance(AuditLogger(), AuditLogger)
