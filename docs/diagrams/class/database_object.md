# Database Objects — Class Diagrams

Class diagrams for the design patterns currently implemented in the **Database Objects** core module:

- Builder Pattern for creating `Table` and `View` objects.
- Strategy Pattern for validating constraints.
- Factory Method for creating `Index` and `DataType` objects.
- Composite Pattern for managing the `Database` and `Schema` hierarchy.
- Repository Pattern for catalog metadata management.

---

## 1. Builder Pattern (Table Creation)

Constructs a `Table` object step by step, separating the build process from the final `Table` object.

```mermaid
classDiagram
    direction LR

    class TableBuilder {
        +set_table_id(table_id: str) TableBuilder
        +add_column(name: str, data_type: DataType | str) TableBuilder
        +add_column_object(column: Column) TableBuilder
        +add_constraint(constraint: Constraint) TableBuilder
        +add_index(index: Index) TableBuilder
        +build() Table
    }

    class Table {
        +table_id: str
        +name: str
        +columns: list
        +constraints: list
        +indexes: list
        +insert(row: Row) bool
        +update(row_id: str, new_values: dict) bool
    }

    class Column {
        +column_id: str
        +name: str
        +data_type: DataType
        +nullable: bool
    }

    class Constraint {
        +constraint_id: str
        +name: str
        +constraint_type: str
    }

    class Index {
        +index_id: str
        +name: str
        +type: str
    }

    TableBuilder ..> Table : builds
    TableBuilder o-- Column : collects
    TableBuilder o-- Constraint : collects
    TableBuilder o-- Index : collects
    Table *-- Column : contains
    Table *-- Constraint : contains
    Table *-- Index : contains
```

`TableBuilder` copies its internal component collections during `build()`, ensuring built `Table` instances remain independent from the builder.

---

## 2. Strategy Pattern (Constraint Validation)

Allows swapping constraint validation logic dynamically using interchangeable strategy classes (`PrimaryKeyStrategy`, `UniqueStrategy`, `ForeignKeyStrategy`, `CheckStrategy`).

```mermaid
classDiagram
    direction LR

    class Table {
        +constraints: list
        +insert(row: Row) bool
        +update(row_id: str, new_values: dict) bool
    }

    class Constraint {
        +constraint_id: str
        +name: str
        +constraint_type: str
        +strategy: ConstraintStrategy
        +set_strategy(strategy: ConstraintStrategy) None
        +validate_row(row: Row, existing_rows: Iterable) bool
        +validate_primary_key(row: Row, key_columns: tuple) bool
        +validate_unique(row: Row, key_columns: tuple, existing_rows: list) bool
        +validate_foreign_key(row: Row, foreign_key_col: str, referenced_keys: set) bool
        +cascade_delete(parent_key_value, child_rows, foreign_key_col) list
        +cascade_update(old_key_value, new_key_value, child_rows, foreign_key_col) int
    }

    class ConstraintStrategy {
        <<abstract>>
        +validate(row: Row, existing_rows: Iterable) bool
    }

    class CheckStrategy {
        +validate(row: Row, existing_rows: Iterable) bool
    }

    class PrimaryKeyStrategy {
        +validate(row: Row, existing_rows: Iterable) bool
    }

    class UniqueStrategy {
        +validate(row: Row, existing_rows: Iterable) bool
    }

    class ForeignKeyStrategy {
        +validate(row: Row, existing_rows: Iterable) bool
        +cascade_delete(parent_key_value, child_rows, foreign_key_col) list
        +cascade_update(old_key_value, new_key_value, child_rows, foreign_key_col) int
    }

    Table o-- Constraint : validates before mutation
    Constraint --> ConstraintStrategy : delegates validation to
    CheckStrategy --|> ConstraintStrategy
    PrimaryKeyStrategy --|> ConstraintStrategy
    UniqueStrategy --|> ConstraintStrategy
    ForeignKeyStrategy --|> ConstraintStrategy
```

`Table` decides when row validation runs. `Constraint` delegates the rule to its selected `ConstraintStrategy`, and `set_strategy()` can replace that rule without changing `Table`.

---

## 3. Factory Method (Index & Data Type Creation)

Uses concrete factory methods to create an `Index` product or a configured `DataType` product.

```mermaid
classDiagram
    direction TB

    class Index {
        +index_id: str
        +name: str
        +type: str
        +columns: tuple
        +unique: bool
        +search(key: object) list
        +insert_key(key: object, row_id: str) bool
        +delete_key(key: object, row_id: str) bool
    }

    class BTreeIndex
    class HashIndex

    class IndexFactory {
        <<abstract>>
        +create_index(index_id: str, name: str, columns: Sequence, unique: bool) Index
    }

    class BTreeIndexFactory {
        +create_index(index_id: str, name: str, columns: Sequence, unique: bool) BTreeIndex
    }

    class HashIndexFactory {
        +create_index(index_id: str, name: str, columns: Sequence, unique: bool) HashIndex
    }

    class DataType {
        +name: str
        +validate(value: object) bool
        +convert(value: object) object
    }

    class DataTypeFactory {
        <<abstract>>
        +create_data_type() DataType
    }

    class IntegerDataTypeFactory {
        +create_data_type() DataType
    }

    class FloatDataTypeFactory {
        +create_data_type() DataType
    }

    class TextDataTypeFactory {
        +create_data_type() DataType
    }

    BTreeIndex --|> Index
    HashIndex --|> Index
    BTreeIndexFactory --|> IndexFactory
    HashIndexFactory --|> IndexFactory
    BTreeIndexFactory ..> BTreeIndex : creates
    HashIndexFactory ..> HashIndex : creates
    IntegerDataTypeFactory --|> DataTypeFactory
    FloatDataTypeFactory --|> DataTypeFactory
    TextDataTypeFactory --|> DataTypeFactory
    IntegerDataTypeFactory ..> DataType : creates
    FloatDataTypeFactory ..> DataType : creates
    TextDataTypeFactory ..> DataType : creates
```

Each concrete factory chooses the product it creates: `BTreeIndexFactory` creates `BTreeIndex`, `HashIndexFactory` creates `HashIndex`, and each data-type factory creates one configured `DataType`.

---

## 4. Composite Pattern (Database Hierarchy)

Organizes `Database`, `Schema`, `Table`, `View`, and `StoredProcedure` into a composite structure for hierarchical catalog management.

```mermaid
classDiagram
    direction TB

    class Database {
        +database_id: str
        +name: str
        +default_schema: str
        +schemas: dict
        +open() bool
        +close() bool
        +create_schema(schema: Schema) bool
        +get_schema(name: str) Schema
        +rename_schema(old_name: str, new_name: str) bool
        +drop_schema(name: str) bool
    }

    class Schema {
        +schema_id: str
        +name: str
        +tables: dict
        +views: dict
        +stored_procedures: dict
        +create_table(table: Table) bool
        +get_table(name: str) Table
        +rename_table(old_name: str, new_name: str) bool
        +drop_table(name: str) bool
        +create_view(view: View) bool
        +get_view(name: str) View
        +drop_view(name: str) bool
        +create_stored_procedure(procedure: StoredProcedure) bool
        +get_stored_procedure(name: str) StoredProcedure
        +drop_stored_procedure(name: str) bool
    }

    class Table
    class View
    class StoredProcedure

    Database *-- Schema : contains
    Schema *-- Table : contains
    Schema *-- View : contains
    Schema *-- StoredProcedure : contains
```

`Database` manages its `Schema` collection, and each `Schema` manages its `Table`, `View`, and `StoredProcedure` collections.

---

## 5. Repository Pattern (Metadata Management)

`CatalogManager` exposes one repository API while `MetadataCacheProtocol` supplies the storage implementation.

```mermaid
classDiagram
    direction LR

    class CatalogManager {
        +metadata_cache: MetadataCacheProtocol
        +register_object(name: str, descriptor: object) bool
        +remove_object(name: str) bool
        +lookup_object(name: str) object
    }

    class MetadataCacheProtocol {
        <<Protocol>>
        +set(name: str, descriptor: object) None
        +remove(name: str) None
        +get(name: str) object | None
    }

    CatalogManager --> MetadataCacheProtocol : uses
```

`lookup_object()` turns a missing cache value into `KeyError`; duplicate registration and missing-removal errors continue to come from the configured cache.

---

## 6. Builder Pattern (View Creation)

Constructs a `View` object step by step, validating query parameters before object instantiation.

```mermaid
classDiagram
    direction LR

    class ViewBuilder {
        +set_view_id(view_id: str) ViewBuilder
        +set_name(name: str) ViewBuilder
        +set_query_definition(query_definition: str) ViewBuilder
        +set_query_executor(query_executor: QueryExecutorProtocol) ViewBuilder
        +set_cached_results(cached_results: object) ViewBuilder
        +build() View
    }

    class View {
        +view_id: str
        +name: str
        +query_definition: str
        +query_executor: QueryExecutorProtocol
        +cached_results: object
        +refresh() bool
    }

    ViewBuilder ..> View : builds
```

`ViewBuilder` validates that both `name` and `query_definition` are provided and non-empty during `build()`.
