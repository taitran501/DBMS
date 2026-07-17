# Database Object Subsystem Unit Test Sequence Diagrams

This document outlines the simplified unit test flows for the **Database Object** subsystem, focusing strictly on the test assertions, SUT calls, and mock expectations.

---

## 1. test_create_database()
Verifies `DatabaseManager` creates and registers a database successfully.

```mermaid
sequenceDiagram
    autonumber
    participant Test as test_create_database()
    participant DBM as DatabaseManager (SUT)
    participant Catalog as CatalogManager (Mock)

    Note over Test: Arrange
    Test->>DBM: Instantiate DatabaseManager with CatalogManager mock

    Note over Test: Act
    Test->>DBM: create_database(name="test_db")
    DBM->>Catalog: register_object("test_db", Database)
    Catalog-->>DBM: True
    DBM-->>Test: Database object

    Note over Test: Assert
    Test->>Test: assert returned_db.name == "test_db"
```

---

## 2. test_create_table()
Tests that a `Schema` initializes a table and registers it with the catalog.

```mermaid
sequenceDiagram
    autonumber
    participant Test as test_create_table()
    participant Schema as Schema (SUT)
    participant Catalog as CatalogManager (Mock)

    Note over Test: Arrange
    Test->>Schema: Instantiate Schema(name="public") with CatalogManager mock

    Note over Test: Act
    Test->>Schema: create_table(name="users")
    Schema->>Catalog: register_object("public.users", Table)
    Catalog-->>Schema: True
    Schema-->>Test: Table object

    Note over Test: Assert
    Test->>Test: assert returned_table.name == "users"
```

---

## 3. test_insert_row()
Verifies that inserting a valid row invokes column validation, partition allocation, and index updates.

```mermaid
sequenceDiagram
    autonumber
    participant Test as test_insert_row()
    participant Table as Table (SUT)
    participant Col as Column (Stub)
    participant Part as Partition (Mock)
    participant Idx as Index (Mock)

    Note over Test: Arrange
    Test->>Table: Instantiate with Column, Partition mock, and Index mock

    Note over Test: Act
    Test->>Table: insert(row=[42])
    Table->>Col: validate(42)
    Col-->>Table: True
    Table->>Part: allocate_space()
    Part-->>Table: True
    Table->>Idx: insert_key(42, "P0:0")
    Idx-->>Table: True
    Table-->>Test: True

    Note over Test: Assert
    Test->>Test: assert insert_result is True
```

---

## 4. test_validate_primary_key()
Tests constraint validation failure when trying to insert a duplicate primary key.

```mermaid
sequenceDiagram
    autonumber
    participant Test as test_validate_primary_key()
    participant Table as Table (SUT)
    participant PK_Const as Constraint (SUT)
    participant Idx as Index (Stub)

    Note over Test: Arrange
    Test->>Idx: Setup Index stub to return existing record pointer for key 100
    Test->>Table: Instantiate Table with PK_Const and Index stub

    Note over Test: Act
    Test->>Table: insert(row=[100])
    Table->>PK_Const: validate_row(row)
    PK_Const->>Idx: search(100)
    Idx-->>PK_Const: ["P0:1"]
    PK_Const-->>Table: False (Validation Failed)
    Table-->>Test: False

    Note over Test: Assert
    Test->>Test: assert insert_result is False
```
