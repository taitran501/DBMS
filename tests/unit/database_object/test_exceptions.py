from dbms.database_object.exceptions import (
    DuplicateDatabaseError,
    DuplicateTriggerError,
    TriggerError,
    UnknownDatabaseError,
)


def test_duplicate_database_error_inherits_exception():
    assert issubclass(DuplicateDatabaseError, Exception)


def test_unknown_database_error_inherits_exception():
    assert issubclass(UnknownDatabaseError, Exception)


def test_trigger_error_inherits_exception():
    assert issubclass(TriggerError, Exception)


def test_duplicate_trigger_error_inherits_exception():
    assert issubclass(DuplicateTriggerError, Exception)
