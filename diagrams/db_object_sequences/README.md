# Database Object Sequence Diagrams

This directory contains the detailed execution workflows for the Database Object management subsystems. These sequence diagrams illustrate the orchestration between various managers (e.g., `TableManager`, `ColumnManager`, `ConstraintManager`, etc.) during both Data Definition (DDL) and Data Manipulation (DML) events.

## Workflows

### 1. [Database & Schema Provisioning](seq_database_schema.mmd)
Demonstrates the creation, validation, and registration of `Database` and `Schema` objects into the System Catalog.

### 2. [Table Definition Workflow](seq_table.mmd)
The core DDL flow for creating a Table. It orchestrates the resolution of data types, the definition of columns, the establishment of constraints, and the creation of indexes before finally registering the table metadata.

### 3. [Advanced Objects](seq_view_proc_trig.mmd)
Covers the creation workflows for advanced database objects, including Views (and their dependency graphs), Stored Procedures (and their executors), and Triggers (and their event bindings).

### 4. [Runtime Execution](seq_runtime.mmd)
Illustrates the runtime execution flow when an application performs data modification (INSERT/UPDATE/DELETE). It shows how table events trigger the `TriggerManager`, how constraints are enforced by the `ConstraintManager`, and how indexes and statistics are dynamically maintained.
