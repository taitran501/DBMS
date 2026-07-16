from dbms.query_processing.statement import Statement
from dbms.query_processing.token import Token


class SqlParser:
    def parse(self, tokens: list[Token]) -> Statement | None:
        return None
