# Database Objects - Applied Design Patterns Sequence Diagrams

This document contains the sequence diagrams detailing the Design Patterns applied to the **Database Objects** core module.

---

## 1. Builder Pattern (Table Creation)

Separates the step-by-step construction of a complex `Table` object from its representation.

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant TableBuilder
    participant DataType
    participant Column
    participant Table

    Client->>TableBuilder: TableBuilder("users")
    Client->>TableBuilder: add_column("id", "INT")
    TableBuilder->>TableBuilder: normalize type name and select converter
    TableBuilder->>DataType: DataType("INT", validator, int)
    DataType-->>TableBuilder: dataType
    TableBuilder->>Column: Column("col_1", "id", dataType)
    Column-->>TableBuilder: column
    Client->>TableBuilder: add_constraint(constraint)
    Client->>TableBuilder: build()
    TableBuilder->>TableBuilder: validate component uniqueness
    TableBuilder->>Table: Table(table_id, name, copied collections)
    Table-->>TableBuilder: tableInstance
    TableBuilder-->>Client: tableInstance

    Note over TableBuilder,Table: Built tables do not share builder collections
```

---

## 2. Strategy Pattern (Constraint Validation)

Encapsulates interchangeability for constraint validation rules (`PrimaryKeyStrategy`, `UniqueStrategy`, `ForeignKeyStrategy`, `CheckStrategy`).

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant Table
    participant Constraint
    participant Strategy as ConstraintStrategy

    Client->>Constraint: Constraint(..., strategy=strategy)
    Client->>Table: insert(row)
    Table->>Table: reject duplicate row_id
    Table->>Table: collect existing_rows

    loop Each constraint
        Table->>Constraint: validate_row(row, existing_rows)
        Constraint->>Strategy: validate(row, existing_rows)
        Strategy-->>Constraint: true or false
        Constraint-->>Table: validation result
    end

    alt A constraint rejects the row
        Table-->>Client: ValueError
        Note over Table: rows and row_count remain unchanged
    else All constraints accept the row
        Table->>Table: rows[row_id] = row
        Table->>Table: row_count += 1
        Table-->>Client: true
    end
```

The validation algorithm can also be replaced without changing `Table`:

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant Constraint
    participant NewStrategy as ConstraintStrategy

    Client->>Constraint: set_strategy(new_strategy)
    Client->>Constraint: validate_row(row, existing_rows)
    Constraint->>NewStrategy: validate(row, existing_rows)
    NewStrategy-->>Constraint: result
    Constraint-->>Client: result
```

`cascade_delete()` and `cascade_update()` remain separate foreign-key referential-action helpers. They are not part of the `Table.insert()` / `Table.update()` Strategy validation sequence above.

---

## 3. Factory Method (Index & Data Type Creation)

Encapsulates object instantiation for Index types (`BTreeIndex`, `HashIndex`) and Data Types (`DataType`).

```mermaid
sequenceDiagram
    autonumber
    participant CatalogManager
    participant IndexFactory
    participant BTreeIndex
    participant Table

    CatalogManager->>IndexFactory: create_index("BTree", name, columns)
    IndexFactory->>BTreeIndex: new BTreeIndex(name, columns)
    BTreeIndex-->>IndexFactory: indexInstance
    IndexFactory-->>CatalogManager: indexInstance
    CatalogManager->>Table: add_index(indexInstance)
```

---

## 4. Composite Pattern (Database Hierarchy)

Composes objects into tree structures to represent `Database` -> `Schema` -> `Table` part-whole hierarchies.

```mermaid
sequenceDiagram
    autonumber
    participant Database
    participant Schema
    participant Table

    Database->>Schema: drop_schema("public")
    loop For each table in schema
        Schema->>Table: drop()
        Table-->>Schema: True
    end
    Schema-->>Database: True
```

---

## 5. Repository Pattern (Metadata Management)

Mediates between the domain and data mapping layers for catalog metadata.

```mermaid
sequenceDiagram
    autonumber
    participant Client
    participant CatalogManager (Repository)
    participant MetadataCache

    Client->>CatalogManager: lookup_object("users")
    CatalogManager->>MetadataCache: get("users")
    MetadataCache-->>CatalogManager: Table Object / None
    CatalogManager-->>Client: Table Object
```

---

## 6. Builder Pattern (View Creation)

Constructs `View` objects from SQL AST queries and dependency checks.

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant ViewBuilder
    participant AST
    participant View

    Client->>ViewBuilder: new ViewBuilder("active_users", sql)
    Client->>ViewBuilder: parse_query()
    ViewBuilder->>AST: construct()
    Client->>ViewBuilder: build()
    ViewBuilder->>View: new View(name, ast)
    View-->>Client: viewInstance
```
