class DuplicateDatabaseError(Exception):
    pass


class UnknownDatabaseError(Exception):
    pass


class DuplicateSchemaError(Exception):
    pass


class UnknownSchemaError(Exception):
    pass


class DatabaseInUseError(Exception):
    pass


class TriggerError(Exception):
    pass


class DuplicateTriggerError(Exception):
    pass
