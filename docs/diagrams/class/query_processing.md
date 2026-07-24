# Query Processing - Class Diagrams

This document contains class diagrams for the applied Design Patterns in the **Query Processing** module.

---

## 1. Interpreter Pattern (SQL Parsing)

`Lexer` tokenizes raw SQL text into `Token` streams, which `SQLParser` parses into an `AST`. Every AST node implements `ASTNode.interpret(context)` to evaluate expressions against row data contexts.

```mermaid
classDiagram
    direction TB

    class ASTNode {
        <<abstract>>
        +interpret(context: dict) Any
    }

    class LiteralNode {
        +value: Any
        +interpret(context: dict) Any
    }

    class IdentifierNode {
        +name: str
        +interpret(context: dict) Any
    }

    class BinaryOpNode {
        +left: ASTNode
        +operator: str
        +right: ASTNode
        +interpret(context: dict) Any
    }

    class SelectNode {
        +table_name: str
        +columns: list[str]
        +where_clause: ASTNode | None
        +interpret(context: dict) Any
    }

    class InsertNode {
        +table_name: str
        +values: list[Any]
        +interpret(context: dict) Any
    }

    class CreateTableNode {
        +table_name: str
        +columns: list[tuple[str, str]]
        +interpret(context: dict) Any
    }

    class AST {
        +root_node: ASTNode
        +interpret(context: dict) Any
        +traverse() list[ASTNode]
    }

    class Lexer {
        +tokenize(sql: str) list[Token]
    }

    class SQLParser {
        +lexer: Lexer
        +parse_sql(sql: str) AST
        +parse(tokens: list[Token]) AST
    }

    LiteralNode --|> ASTNode
    IdentifierNode --|> ASTNode
    BinaryOpNode --|> ASTNode
    SelectNode --|> ASTNode
    InsertNode --|> ASTNode
    CreateTableNode --|> ASTNode
    AST *-- ASTNode : wraps root
    SQLParser --> Lexer : uses
    SQLParser ..> AST : constructs
```

`SelectNode`, `BinaryOpNode`, `IdentifierNode`, and `LiteralNode` form the expression tree evaluated via `interpret()`.
