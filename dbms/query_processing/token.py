from dbms.query_processing.token_type import TokenType


class Token:
    def __init__(self, token_type: TokenType, value: str, position: int) -> None:
        self.token_type = token_type
        self.value = value
        self.position = position
