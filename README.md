# Mini DBMS - Slotted-Page Database Management System

A Python-based lightweight Database Management System (DBMS) architecture featuring slotted-page storage engine, ACID transaction management with multiple isolation levels, cost-based query optimization, security access control, and recovery subsystems.

## 🚀 Current Status & Progress

The project is currently focused on **Database Management** (Schema, Table, Column, Index, Constraint definition and cataloging). 
* **Database Objects**: Fully integrated schema creation, index definition, and basic catalog updates.
* **Other Subsystems**: (Storage Engine, Transactions, Security, Query Processing, Durability) are initialized with core components or mock structures to facilitate end-to-end flow and unit/integration testing.

---

## 🧠 System Architecture & Design


### 1. Mindmap (Level 2 Overview)

The high-level visual representation of the subsystems within the Mini DBMS:

![Mindmap Level 2](diagrams/mindmap_level_2.png)


---

### 2. Class Diagram Overview


The architectural components and how they interact conceptually:


```mermaid
classDiagram
direction LR

    class DBMS {
    }
    class DatabaseObject
    class Transaction
    class StorageEngine
    class QueryProcessing
    class Durability
    class SecurityAccessControl
    class Performance
    class AdministrationOperations

    DBMS *-- DatabaseObject
    DBMS *-- Transaction
    DBMS *-- StorageEngine
    DBMS *-- QueryProcessing
    DBMS *-- Durability
    DBMS *-- SecurityAccessControl
    DBMS *-- Performance
    DBMS *-- AdministrationOperations

    QueryProcessing --> DatabaseObject : reads schema / metadata
    QueryProcessing --> SecurityAccessControl : checks permissions
    QueryProcessing --> Transaction : executes within
    QueryProcessing --> StorageEngine : requests data access

    Transaction --> StorageEngine : controls read / write
    Transaction --> Durability : commit / rollback safety
    Transaction --> SecurityAccessControl : validates session context

    StorageEngine --> DatabaseObject : stores tables / indexes
    StorageEngine --> Durability : writes logs / checkpoints
    StorageEngine --> Performance : exposes storage metrics

    Durability --> StorageEngine : restores data pages
    Durability --> Transaction : recovers transactions

    SecurityAccessControl --> DatabaseObject : grants object permissions
    SecurityAccessControl --> AdministrationOperations : audit / policy logs

    Performance --> QueryProcessing : query tuning feedback
    Performance --> StorageEngine : memory / IO tuning
    Performance --> DatabaseObject : index strategy

    AdministrationOperations --> SecurityAccessControl : user / role operations
    AdministrationOperations --> Durability : backup / restore jobs
    AdministrationOperations --> Performance : monitoring / alerts
    AdministrationOperations --> StorageEngine : configuration management
```

---

### 3. General Sequence Diagram (Execution Flow)


The end-to-end request processing flow, from query parsing, authentication, transaction boundaries, execution to persistence:


```mermaid
sequenceDiagram
    autonumber

    actor Client

    participant DBMS as DatabaseEngine
    participant SAC as SecurityAccessControlService
    participant QP as QueryProcessingService
    participant DO as DatabaseObjectService
    participant TX as TransactionManager
    participant SE as StorageEngine
    participant DUR as DurabilityManager
    participant AO as AdministrationOperationsService

    Client->>DBMS: Submit SQL request

    DBMS->>SAC: Validate session
    SAC-->>DBMS: Valid session

    DBMS->>QP: Process request

    QP->>DO: Request object metadata
    DO-->>QP: Return object metadata

    QP->>SAC: Check access permission
    SAC-->>QP: Access granted

    QP->>TX: Start transaction
    TX-->>QP: Transaction context

    QP->>SE: Execute operation
    SE-->>QP: Operation result

    alt Success
        QP->>TX: Commit transaction

        opt Persistent changes
            TX->>DUR: Persist transaction
            DUR-->>TX: Persistence confirmed
        end

        TX-->>QP: Commit completed
        QP-->>DBMS: Request result
        DBMS-->>Client: Return result
        DBMS->>AO: Record success
    else Failure
        QP->>TX: Rollback transaction
        TX->>SE: Revert changes
        SE-->>TX: Changes reverted
        TX-->>QP: Rollback completed

        QP-->>DBMS: Error result
        DBMS-->>Client: Return error
        DBMS->>AO: Record failure
    end
```

---

### 4. Database Object Sequence Diagrams

The complex database object management workflows have been decomposed into 4 focused sequence diagrams, located in `diagrams/db_object_sequences/`:

For detailed workflow diagrams, please refer to the **[Database Object Sequences Directory](diagrams/db_object_sequences/)**:

1. **[Database & Schema Provisioning](diagrams/db_object_sequences/seq_database_schema.mmd)**: Details the creation and registration of logical namespaces.
2. **[Table Definition Workflow](diagrams/db_object_sequences/seq_table.mmd)**: Orchestrates columns, data types, and constraint definitions.
3. **[Advanced Objects](diagrams/db_object_sequences/seq_view_proc_trig.mmd)**: The DDL workflows for Views, Stored Procedures, and Triggers.
4. **[Runtime Execution](diagrams/db_object_sequences/seq_runtime.mmd)**: Shows how data manipulation events interact with Triggers, Constraints, and Indexes.
---

### 5. Database Object Modules (Decomposed)

The **Database Object** domain has been fully decomposed into the following single-responsibility management modules, reflecting the design in the Level 5 Mindmap:

- **Database Management**: `DatabaseManager`, `DatabaseDescriptor`, `DatabaseConfiguration`, `DatabaseRegistry`
- **Schema Management**: `SchemaManager`, `SchemaDescriptor`, `SchemaCatalog`, `SchemaOwnershipPolicy`, `SchemaMigrationLedger`
- **Table Management**: `TableManager`, `TableDescriptor`, `TableOrganization`, `TableScope`
- **View Management**: `ViewManager`, `ViewDescriptor`, `ViewDependencyGraph`
- **Relationship Management**: `RelationshipManager`, `RelationshipDescriptor`, `ReferentialActionPolicy`
- **Column Management**: `ColumnManager`, `ColumnDescriptor`, `ColumnRuleSet`
- **Constraint Management**: `ConstraintManager`, `ConstraintDescriptor`, `ConstraintEnforcer`
- **Data Type Management**: `DataTypeManager`, `TypeValidator`, `TypeConverter`
- **Index Management**: `IndexManager`, `IndexDescriptor`, `IndexAccessMethod`, `IndexOrganization`, `IndexMaintainer`
- **Stored Procedure**: `StoredProcedureManager`, `ProcedureDescriptor`, `ProcedureExecutor`
- **Trigger Management**: `TriggerManager`, `TriggerDescriptor`, `TriggerEventBinding`, `TriggerExecutor`
- **Metadata Management**: `MetadataManager`, `SystemCatalog`, `DependencyManager`, `StatisticsManager`

---

## 🛠️ Installation & Running Tests

Ensure you have Python 3.10+ installed.

### 1. Install Dependencies
This project uses `pytest` for tests.
```bash
pip install pytest
```

### 2. Run Tests
Execute the unit and integration tests to verify the DBMS subsystems:
```bash
pytest
```
