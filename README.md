# DBMS

Python DBMS architecture project. The repository is currently at the class-design stage: selected core classes define their initial attributes and method stubs, while business logic has not been implemented yet.

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
direction TB

    class DBMS {
        +database_object_manager: DatabaseObjectManager
        +transaction_manager: TransactionManager
        +storage_engine: StorageEngine
        +durability_manager: DurabilityManager
        +query_processor: QueryProcessor
        +start() bool
        +shutdown() bool
        +execute(sql: str, session: object) object
    }
    class DatabaseObjectManager {
        +metadata_manager: MetadataManager
        +get_object(name: str) object
        +object_exists(name: str) bool
    }
    class TransactionManager {
        +begin() Transaction
        +commit(transaction: Transaction) bool
        +rollback(transaction: Transaction) bool
    }
    class Transaction {
        +transaction_id: int
        +status: TransactionStatus
    }
    class TransactionStatus {
        <<enumeration>>
        ACTIVE
        COMMITTED
        ROLLED_BACK
    }
    class StorageEngine {
        +buffer_pool: BufferPool
        +read(page_id: int) object
        +write(value: object) bool
        +delete(record_id: int) bool
        +revert(transaction_id: int) bool
    }
    class DurabilityManager {
        +transaction_log_manager: TransactionLogManager
        +recovery_manager: RecoveryManager
        +persist(transaction_id: int) bool
        +recover() bool
    }
    class QueryProcessor {
        +sql_parser: SqlParser
        +query_validator: QueryValidator
        +query_executor: QueryExecutor
        +process(sql: str, session: object) object
    }
    class BufferPool {
        +capacity: int
        +get_page(page_id: int) Page
        +put_page(page: Page) bool
        +flush() bool
    }
    class Page {
        +page_id: int
        +data: bytes
        +read() bytes
        +write(data: bytes) bool
    }
    class Record {
        +record_id: int
        +values: dict
    }
    class TransactionLogManager {
        +append(record: LogRecord) bool
        +read_entries(transaction_id: int) list
    }
    class RecoveryManager {
        +transaction_log_manager: TransactionLogManager
        +recover() bool
        +rollback(transaction_id: int) bool
    }
    class LogRecord {
        +transaction_id: int
        +operation: str
        +before_value: object
        +after_value: object
    }
    class SqlParser {
        +parse(tokens: list) Statement
    }
    class Lexer {
        +tokenize(sql: str) list~Token~
    }
    class Token {
        +token_type: TokenType
        +value: str
        +position: int
    }
    class TokenType {
        <<enumeration>>
        KEYWORD
        IDENTIFIER
        LITERAL
        OPERATOR
        PUNCTUATION
        END_OF_INPUT
    }
    class Statement {
        +statement_type: str
    }
    class SelectStatement {
        +table_name: str
        +columns: list~str~
        +where: object
    }
    class QueryValidator {
        +validate(statement: Statement) bool
    }
    class QueryExecutor {
        +execute(statement: Statement, transaction: object) object
    }
    class MetadataManager {
        +system_catalog: SystemCatalog
        +register(name: str, descriptor: object) bool
        +get(name: str) object
        +remove(name: str) bool
    }
    class SystemCatalog {
        +register(name: str, descriptor: object) bool
        +find(name: str) object
        +remove(name: str) bool
    }
    class TableDescriptor {
        +name: str
        +schema_name: str
    }
    class ColumnDescriptor {
        +name: str
        +data_type: str
        +nullable: bool
    }

    DBMS *-- DatabaseObjectManager
    DBMS *-- TransactionManager
    DBMS *-- StorageEngine
    DBMS *-- DurabilityManager
    DBMS *-- QueryProcessor

    DatabaseObjectManager *-- MetadataManager
    MetadataManager *-- SystemCatalog

    TransactionManager --> Transaction
    Transaction --> TransactionStatus

    StorageEngine *-- BufferPool
    BufferPool o-- Page

    DurabilityManager *-- TransactionLogManager
    DurabilityManager *-- RecoveryManager
    TransactionLogManager o-- LogRecord
    RecoveryManager --> TransactionLogManager

    QueryProcessor *-- SqlParser
    QueryProcessor *-- QueryValidator
    QueryProcessor *-- QueryExecutor
    Lexer --> Token
    Token --> TokenType
    SqlParser --> Token
    SqlParser --> Statement
    QueryValidator --> Statement
    QueryExecutor --> Statement
    SelectStatement --|> Statement

```

---

## 🛠️ Installation & Running Tests

Ensure you have Python 3.10+ installed.

### 1. Install Dependencies

```bash
python -m pip install -r requirements-dev.txt
```

### 2. Run Tests
Run the current core class design tests:
```bash
python -m pytest -q
```
