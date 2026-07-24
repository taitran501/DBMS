from typing import Any

from dbms.query_processing.ast import (
    AST,
    ASTNode,
    BinaryOpNode,
    CreateTableNode,
    IdentifierNode,
    InsertNode,
    LiteralNode,
    SelectNode,
)
from dbms.query_processing.lexer import Lexer
from dbms.query_processing.token import Token
from dbms.query_processing.token_type import TokenType


class SQLParser:
    """Recursive-descent SQL Parser that constructs an Abstract Syntax Tree (AST)."""

    def __init__(self, lexer: Lexer | None = None) -> None:
        self.lexer = lexer or Lexer()

    def parse_sql(self, sql: str) -> AST:
        """Convenience method to tokenize and parse a raw SQL string into an AST."""
        tokens = self.lexer.tokenize(sql)
        return self.parse(tokens)

    def parse(self, tokens: list[Token]) -> AST:
        """Parse a list of Tokens into an AST."""
        if not tokens or tokens[0].token_type == TokenType.END_OF_INPUT:
            raise ValueError("Empty or invalid token stream")

        pos = 0
        first_token = tokens[pos]

        if first_token.token_type == TokenType.KEYWORD and first_token.value == "SELECT":
            root = self._parse_select(tokens, pos)
        elif first_token.token_type == TokenType.KEYWORD and first_token.value == "INSERT":
            root = self._parse_insert(tokens, pos)
        elif first_token.token_type == TokenType.KEYWORD and first_token.value == "CREATE":
            root = self._parse_create_table(tokens, pos)
        else:
            raise ValueError(f"Unsupported SQL command starting with: {first_token.value}")

        return AST(root)

    def _parse_select(self, tokens: list[Token], pos: int) -> SelectNode:
        # Expected: SELECT col1, col2 FROM table [WHERE left op right]
        pos += 1  # consume SELECT
        columns: list[str] = []

        # Parse column list until FROM
        while pos < len(tokens) and not (tokens[pos].token_type == TokenType.KEYWORD and tokens[pos].value == "FROM"):
            tok = tokens[pos]
            if tok.token_type in (TokenType.IDENTIFIER, TokenType.OPERATOR):
                columns.append(str(tok.value))
            elif tok.token_type == TokenType.PUNCTUATION and tok.value == ",":
                pass
            pos += 1

        if pos >= len(tokens) or tokens[pos].value != "FROM":
            raise ValueError("Expected FROM keyword in SELECT query")

        pos += 1  # consume FROM
        if pos >= len(tokens) or tokens[pos].token_type != TokenType.IDENTIFIER:
            raise ValueError("Expected table name after FROM")

        table_name = str(tokens[pos].value)
        pos += 1

        where_clause: ASTNode | None = None
        if pos < len(tokens) and tokens[pos].token_type == TokenType.KEYWORD and tokens[pos].value == "WHERE":
            pos += 1  # consume WHERE
            where_clause, _ = self._parse_expression(tokens, pos)

        return SelectNode(table_name=table_name, columns=columns, where_clause=where_clause)

    def _parse_insert(self, tokens: list[Token], pos: int) -> InsertNode:
        # Expected: INSERT INTO table VALUES (val1, val2)
        pos += 1  # consume INSERT
        if pos < len(tokens) and tokens[pos].token_type == TokenType.KEYWORD and tokens[pos].value == "INTO":
            pos += 1

        if pos >= len(tokens) or tokens[pos].token_type != TokenType.IDENTIFIER:
            raise ValueError("Expected table name in INSERT statement")

        table_name = str(tokens[pos].value)
        pos += 1

        if pos >= len(tokens) or tokens[pos].value != "VALUES":
            raise ValueError("Expected VALUES keyword in INSERT statement")

        pos += 1
        values: list[Any] = []
        if pos < len(tokens) and tokens[pos].value == "(":
            pos += 1
            while pos < len(tokens) and tokens[pos].value != ")":
                tok = tokens[pos]
                if tok.token_type == TokenType.LITERAL or tok.token_type == TokenType.IDENTIFIER:
                    values.append(tok.value)
                pos += 1

        return InsertNode(table_name=table_name, values=values)

    def _parse_create_table(self, tokens: list[Token], pos: int) -> CreateTableNode:
        # Expected: CREATE TABLE table (col1 type1, col2 type2)
        pos += 1  # consume CREATE
        if pos < len(tokens) and tokens[pos].value == "TABLE":
            pos += 1

        if pos >= len(tokens) or tokens[pos].token_type != TokenType.IDENTIFIER:
            raise ValueError("Expected table name in CREATE TABLE statement")

        table_name = str(tokens[pos].value)
        pos += 1

        columns: list[tuple[str, str]] = []
        if pos < len(tokens) and tokens[pos].value == "(":
            pos += 1
            while pos < len(tokens) and tokens[pos].value != ")":
                tok = tokens[pos]
                if tok.token_type == TokenType.IDENTIFIER:
                    col_name = str(tok.value)
                    pos += 1
                    col_type = "TEXT"
                    if pos < len(tokens) and tokens[pos].token_type == TokenType.KEYWORD:
                        col_type = str(tokens[pos].value)
                        pos += 1
                    columns.append((col_name, col_type))
                    continue
                pos += 1

        return CreateTableNode(table_name=table_name, columns=columns)

    def _parse_expression(self, tokens: list[Token], pos: int) -> tuple[ASTNode, int]:
        # Simple binary expression parse: identifier op literal
        left_tok = tokens[pos]
        left_node: ASTNode
        if left_tok.token_type == TokenType.IDENTIFIER:
            left_node = IdentifierNode(str(left_tok.value))
        else:
            left_node = LiteralNode(left_tok.value)
        pos += 1

        if pos < len(tokens) and tokens[pos].token_type == TokenType.OPERATOR:
            op = str(tokens[pos].value)
            pos += 1
            right_tok = tokens[pos]
            right_node: ASTNode
            if right_tok.token_type == TokenType.IDENTIFIER:
                right_node = IdentifierNode(str(right_tok.value))
            else:
                right_node = LiteralNode(right_tok.value)
            pos += 1
            return BinaryOpNode(left_node, op, right_node), pos

        return left_node, pos
