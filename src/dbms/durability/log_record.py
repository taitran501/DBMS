class LogRecord:
    def __init__(
        self,
        transaction_id: int,
        operation: str,
        before_value: object | None = None,
        after_value: object | None = None,
    ) -> None:
        self.transaction_id = transaction_id
        self.operation = operation
        self.before_value = before_value
        self.after_value = after_value
