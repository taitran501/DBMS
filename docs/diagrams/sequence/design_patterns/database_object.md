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
    participant Column
    participant Table

    Client->>TableBuilder: new TableBuilder("users")
    Client->>TableBuilder: add_column("id", INT)
    TableBuilder->>Column: new Column("col_1", "id", INT)
    Client->>TableBuilder: add_constraint(PrimaryKey("id"))
    Client->>TableBuilder: build()
    TableBuilder->>Table: new Table(table_id, name, columns, constraints, indexes)
    Table-->>TableBuilder: tableInstance
    TableBuilder-->>Client: tableInstance
```

---

## 2. Strategy Pattern (Constraint Validation)

Encapsulates interchangeability for constraint validation rules (`PrimaryKeyStrategy`, `UniqueStrategy`, `ForeignKeyStrategy`, `CheckStrategy`).

```mermaid
sequenceDiagram
    autonumber
    participant Client
    participant Constraint (Context)
    participant CheckStrategy
    participant PrimaryKeyStrategy
    participant UniqueStrategy
    participant ForeignKeyStrategy

    alt CHECK Constraint Validation
        Client->>Constraint: validate_row(row)
        Constraint->>CheckStrategy: validate(row, validation_rule)
        CheckStrategy-->>Constraint: True / False
    else PRIMARY KEY Constraint Validation
        Client->>Constraint: validate_primary_key(row, key_columns)
        Constraint->>PrimaryKeyStrategy: validate_primary_key(row, key_columns)
        PrimaryKeyStrategy-->>Constraint: True / False
    else UNIQUE Constraint Validation
        Client->>Constraint: validate_unique(row, key_columns, existing_rows)
        Constraint->>UniqueStrategy: validate_unique(row, key_columns, existing_rows)
        UniqueStrategy-->>Constraint: True / False
    else FOREIGN KEY Cascade Actions
        Client->>Constraint: cascade_delete(parent_key_value, child_rows, foreign_key_col)
        Constraint->>ForeignKeyStrategy: cascade_delete(parent_key_value, child_rows, foreign_key_col)
        ForeignKeyStrategy-->>Constraint: deleted_ids
    end
    Constraint-->>Client: result
```

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
