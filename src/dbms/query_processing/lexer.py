import re

from dbms.query_processing.token import Token
from dbms.query_processing.token_type import TokenType

KEYWORDS = {
    "SELECT",
    "INSERT",
    "INTO",
    "VALUES",
    "CREATE",
    "TABLE",
    "FROM",
    "WHERE",
    "AND",
    "OR",
    "INT",
    "TEXT",
}


class Lexer:
    """Tokenizer for converting raw SQL query strings into a list of Tokens."""

    def tokenize(self, sql: str) -> list[Token]:
        tokens: list[Token] = []
        position = 0
        length = len(sql)

        while position < length:
            char = sql[position]

            if char.isspace():
                position += 1
                continue

            # Punctuation
            if char in (",", "(", ")", ";"):
                tokens.append(Token(TokenType.PUNCTUATION, char, position))
                position += 1
                continue

            # Operators (=, >, <, >=, <=, !=)
            if char in ("=", ">", "<", "!"):
                if position + 1 < length and sql[position : position + 2] in (">=", "<=", "!="):
                    op = sql[position : position + 2]
                    tokens.append(Token(TokenType.OPERATOR, op, position))
                    position += 2
                else:
                    tokens.append(Token(TokenType.OPERATOR, char, position))
                    position += 1
                continue

            # String literals: 'hello' or "hello"
            if char in ("'", '"'):
                quote = char
                start_pos = position
                position += 1
                str_val = ""
                while position < length and sql[position] != quote:
                    str_val += sql[position]
                    position += 1
                if position < length and sql[position] == quote:
                    position += 1
                tokens.append(Token(TokenType.LITERAL, str_val, start_pos))
                continue

            # Numeric literals: 123, 45.6
            if char.isdigit():
                start_pos = position
                num_str = ""
                while position < length and (sql[position].isdigit() or sql[position] == "."):
                    num_str += sql[position]
                    position += 1
                val = float(num_str) if "." in num_str else int(num_str)
                tokens.append(Token(TokenType.LITERAL, val, start_pos))
                continue

            # Keywords and Identifiers: e.g. SELECT, users, age
            if char.isalpha() or char == "_":
                start_pos = position
                ident_str = ""
                while position < length and (sql[position].isalnum() or sql[position] == "_"):
                    ident_str += sql[position]
                    position += 1

                upper_ident = ident_str.upper()
                if upper_ident in KEYWORDS:
                    tokens.append(Token(TokenType.KEYWORD, upper_ident, start_pos))
                else:
                    tokens.append(Token(TokenType.IDENTIFIER, ident_str, start_pos))
                continue

            # Fallback for unrecognized character
            tokens.append(Token(TokenType.PUNCTUATION, char, position))
            position += 1

        tokens.append(Token(TokenType.END_OF_INPUT, "", position))
        return tokens
