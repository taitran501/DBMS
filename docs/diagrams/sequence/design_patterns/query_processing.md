# Query Processing - Applied Design Patterns Sequence Diagrams

This document contains the sequence diagrams detailing the Design Patterns applied to the **Query Processing** core module.

---

## 1. Interpreter Pattern (SQL Parsing)

Converts a raw SQL string into tokens via `Lexer`, parses tokens into an `AST` via `SQLParser`, and evaluates expressions dynamically against row data using `interpret(context)`.

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant Parser as SQLParser
    participant Lexer
    participant AST
    participant Node as SelectNode/BinaryOpNode

    Client->>Parser: parse_sql("SELECT id, name FROM users WHERE age > 18")
    Parser->>Lexer: tokenize(sql)
    Lexer-->>Parser: tokens: list[Token]
    Parser->>Parser: parse tokens recursively
    Parser->>AST: AST(SelectNode)
    AST-->>Parser: astInstance
    Parser-->>Client: astInstance

    Client->>AST: interpret(context={"age": 25})
    AST->>Node: interpret(context)
    Node-->>AST: True
    AST-->>Client: True
```

The Interpreter pattern separates syntax tokenization, AST construction, and context evaluation into distinct, testable layers.
