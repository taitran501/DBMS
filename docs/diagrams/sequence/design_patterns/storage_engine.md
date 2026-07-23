# Storage Engine - Design Pattern Sequences

## 1. Data Mapper (Record Read/Write)

`RecordMapper` converts between the database-object `Row` and a storage `Record` byte payload. `RecordManager` owns page-slot locations and releases the page after each operation.

### Insert a row

```mermaid
sequenceDiagram
    participant Client
    participant Manager as RecordManager
    participant Mapper as RecordMapper
    participant Pages as PageManager
    participant Page

    Client->>Manager: insert_row(row)
    Manager->>Mapper: serialize(row)
    Mapper-->>Manager: payload: bytes
    Manager->>Pages: get_page_with_free_space(len(payload))
    Pages-->>Manager: Page
    Manager->>Page: insert_tuple(payload)
    Page-->>Manager: slot_id
    Manager->>Pages: release_page(page_id)
    Manager-->>Client: "page_id:slot_id"
```

### Read a row

```mermaid
sequenceDiagram
    participant Client
    participant Manager as RecordManager
    participant Pages as PageManager
    participant Page
    participant Mapper as RecordMapper

    Client->>Manager: read_row("page_id:slot_id")
    Manager->>Pages: get_page(page_id)
    Pages-->>Manager: Page
    Manager->>Page: read_tuple(slot_id)
    Page-->>Manager: payload: bytes
    Manager->>Mapper: deserialize(payload)
    Mapper-->>Manager: Row
    Manager->>Pages: release_page(page_id)
    Manager-->>Client: Row
```

If a page or slot does not exist, `RecordManager` raises `RecordNotFoundError`. This implementation has no disk I/O yet; `FileManager` and `BufferPool` are separate planned work.
