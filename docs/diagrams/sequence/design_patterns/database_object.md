# Database Objects - Applied Design Patterns Sequence Diagrams

This document contains the sequence diagrams detailing the Design Patterns applied to the **Database Objects** core module.

---

## 1. Builder Pattern (Table Creation)

Constructs a `Table` object step by step, separating the build process from the final `Table` object.

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
```

---

## 2. Strategy Pattern (Constraint Validation)

Allows swapping constraint validation logic dynamically using interchangeable strategy classes (`PrimaryKeyStrategy`, `UniqueStrategy`, `ForeignKeyStrategy`, `CheckStrategy`).

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
    else All constraints accept the row
        Table->>Table: rows[row_id] = row
        Table->>Table: row_count += 1
        Table-->>Client: true
    end
```

The validation strategy can be dynamically replaced on a constraint without altering the `Table` implementation:

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

Foreign key referential actions (`cascade_delete` and `cascade_update`) run separately from the row validation sequence above.

---

## 3. Factory Method (Index & Data Type Creation)

Uses concrete factory methods to create an `Index` product or a configured `DataType` product.

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant BTreeIndexFactory
    participant BTreeIndex
    participant IntegerDataTypeFactory
    participant DataType
    participant TableBuilder
    participant Column

    Client->>BTreeIndexFactory: create_index(id, name, columns, unique)
    BTreeIndexFactory->>BTreeIndex: BTreeIndex(id, name, columns, unique)
    BTreeIndex-->>BTreeIndexFactory: index
    BTreeIndexFactory-->>Client: index
    Client->>TableBuilder: add_index(index)
    Client->>IntegerDataTypeFactory: create_data_type()
    IntegerDataTypeFactory->>DataType: DataType("INT", validator, int)
    DataType-->>IntegerDataTypeFactory: dataType
    IntegerDataTypeFactory-->>Client: dataType
    Client->>TableBuilder: add_column("age", dataType)
    TableBuilder->>Column: Column(..., dataType)
```

---

## 4. Composite Pattern (Database Hierarchy)

Organizes `Database`, `Schema`, and child objects into a hierarchical structure for schema and component lookup and management.

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant Database
    participant Schema

    Client->>Database: drop_schema("application")
    Database->>Database: verify name is not default_schema
    Database->>Database: remove schema from schemas dict
    Database-->>Client: True
```

---

## 5. Repository Pattern (Metadata Management)

Provides a single API for storing, retrieving, and removing catalog metadata through an injected cache abstraction.

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant CatalogManager
    participant MetadataCache

    Client->>CatalogManager: register_object("public.users", descriptor)
    CatalogManager->>MetadataCache: set("public.users", descriptor)
    MetadataCache-->>CatalogManager: stored
    CatalogManager-->>Client: true

    Client->>CatalogManager: lookup_object("public.users")
    CatalogManager->>MetadataCache: get("public.users")
    alt Metadata exists
        MetadataCache-->>CatalogManager: descriptor
        CatalogManager-->>Client: descriptor
    else Metadata is missing
        MetadataCache-->>CatalogManager: None
        CatalogManager-->>Client: KeyError
    end

    Client->>CatalogManager: remove_object("public.users")
    CatalogManager->>MetadataCache: remove("public.users")
    MetadataCache-->>CatalogManager: removed
    CatalogManager-->>Client: true
```

---

## 6. Builder Pattern (View Creation)

Constructs a `View` object step by step, separating complex view construction parameters (query definition, view ID, query executor contract, and cached query results) from the domain `View` entity.

### Feature Workflow & Validation:
1. **Step-by-Step Configuration**: The client instantiates `ViewBuilder` with a view name and SQL query definition, then chains optional configuration methods (`set_view_id()`, `set_query_executor()`, `set_cached_results()`).
2. **Pre-Construction Validation**: Calling `.build()` validates that `name` and `query_definition` are non-empty strings, raising `ValueError` on invalid state.
3. **View Instantiation**: Automatically resolves a default `view_id` (`view_<name>`) if unassigned, then instantiates and returns the immutable `View` object.

```mermaid
sequenceDiagram
    autonumber
    actor Client
    participant ViewBuilder
    participant View

    Client->>ViewBuilder: ViewBuilder("active_users", "SELECT * FROM users WHERE active = 1")
    Client->>ViewBuilder: set_view_id("v_001")
    Client->>ViewBuilder: set_query_executor(executor)
    Client->>ViewBuilder: set_cached_results(cached_data)
    Client->>ViewBuilder: build()
    ViewBuilder->>ViewBuilder: validate name and query_definition non-empty
    ViewBuilder->>ViewBuilder: resolve view_id ("v_001" or default "view_active_users")
    ViewBuilder->>View: View("v_001", "active_users", query_definition, executor, cached_data)
    View-->>ViewBuilder: viewInstance
    ViewBuilder-->>Client: viewInstance
```


