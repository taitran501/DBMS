from dbms.transaction.transaction_status import TransactionStatus


class Transaction:
    def __init__(self, transaction_id: int, status: TransactionStatus) -> None:
        self.transaction_id = transaction_id
        self.status = status
