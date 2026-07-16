from enum import Enum, auto


class TransactionStatus(Enum):
    ACTIVE = auto()
    COMMITTED = auto()
    ROLLED_BACK = auto()
