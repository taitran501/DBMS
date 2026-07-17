# Query Processing Subsystem Unit Test Sequence Diagrams

This document outlines the simplified unit test flows for the **Query Processing** subsystem, focusing strictly on the test assertions, SUT calls, and mock expectations.

---

## 1. test_sql_parser_parse()
Verifies that `SQLParser` utilizes the `Lexer` and returns the expected AST.

```mermaid
sequenceDiagram
    autonumber
    participant Test as test_sql_parser_parse()
    participant Parser as SQLParser (SUT)
    participant Lexer as Lexer (Mock)

    Note over Test: Act
    Test->>Parser: parse("SELECT name FROM users")
    Parser->>Lexer: tokenize()
    Lexer-->>Parser: [Token(SELECT), Token(name), Token(FROM), Token(users)]
    Parser-->>Test: AST object

    Note over Test: Assert
    Test->>Test: assert AST.root_node.type == "SelectNode"
```

---

## 2. test_query_optimizer_optimize()
Tests that `QueryOptimizer` transforms logical operators and queries statistics to produce a physical plan.

```mermaid
sequenceDiagram
    autonumber
    participant Test as test_query_optimizer_optimize()
    participant Optimizer as QueryOptimizer (SUT)
    participant Stats as StatisticsManager (Mock)

    Note over Test: Arrange
    Test->>Optimizer: Initialize with StatisticsManager mock returning cost=1.5

    Note over Test: Act
    Test->>Optimizer: optimize(LogicalPlan)
    Optimizer->>Stats: estimate_cardinality()
    Stats-->>Optimizer: 100.0
    Optimizer->>Stats: estimate_cost(LogicalScan)
    Stats-->>Optimizer: 1.5
    Optimizer-->>Test: PhysicalPlan object

    Note over Test: Assert
    Test->>Test: assert physical_plan.operators[0].type == "PhysicalIndexScan"
```

---

## 3. test_query_executor_execute_select()
Verifies that `QueryExecutor` executes a SELECT plan by looking up table metadata and reading tuples from storage.

```mermaid
sequenceDiagram
    autonumber
    participant Test as test_query_executor_execute_select()
    participant Exec as QueryExecutor (SUT)
    participant Catalog as CatalogManager (Stub)
    participant Storage as StorageEngine (Mock)

    Note over Test: Arrange
    Test->>Catalog: Register table "users" with page 0
    Test->>Storage: Configure read_page(0) mock to return page with tuple (42, "Bob")
    Test->>Exec: Initialize with Catalog stub and StorageEngine mock

    Note over Test: Act
    Test->>Exec: execute(PhysicalPlan)
    Exec->>Catalog: lookup_object("users")
    Catalog-->>Exec: Table metadata
    Exec->>Storage: read_page(0)
    Storage-->>Exec: Page object (containing "Bob")
    Exec-->>Test: results ([(42, "Bob")])

    Note over Test: Assert
    Test->>Test: assert results == [(42, "Bob")]
```

---

## 4. test_query_executor_execute_insert_transactional()
Tests that writing data via `QueryExecutor` correctly coordinates lock acquisition, WAL writing, page modification, and transaction commit.

```mermaid
sequenceDiagram
    autonumber
    participant Test as test_query_executor_execute_insert_transactional()
    participant Exec as QueryExecutor (SUT)
    participant TxManager as TransactionManager (SUT)
    participant LockManager as LockManager (Mock)
    participant WALManager as WALManager (Mock)

    Note over Test: Act
    Test->>TxManager: begin_transaction()
    TxManager-->>Test: Transaction object

    Test->>Exec: execute(PhysicalPlan, Transaction)
    Exec->>LockManager: acquire_lock(Transaction, "users", "EXCLUSIVE")
    LockManager-->>Exec: True
    Exec->>WALManager: append(LogRecord)
    WALManager-->>Exec: True
    Exec-->>Test: True

    Test->>TxManager: commit(Transaction)
    TxManager->>WALManager: flush()
    WALManager-->>TxManager: True
    TxManager->>LockManager: release_lock(Transaction, "users")
    LockManager-->>TxManager: True
    TxManager-->>Test: True

    Note over Test: Assert
    Test->>Test: assert commit_success is True
```
