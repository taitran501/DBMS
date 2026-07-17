from dbms.transaction.transaction import Transaction


class TransactionManager:
    def begin_transaction(self) -> Transaction | None:
        return None

    def commit(self, transaction: Transaction) -> bool:
        return True

    def rollback(self, transaction: Transaction) -> bool:
        return True
