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

If a page or slot does not exist, `RecordManager` raises `RecordNotFoundError`. `PageManager` still owns in-memory pages; it is not yet connected to the File Access adapter.

---

## 2. Adapter (File Access)

`FileManager` wraps filesystem paths and binary file access behind root-relative DBMS methods. The same adapter implements `PageStoreProtocol` for storing complete serialized pages.

### Write and load a page

```mermaid
sequenceDiagram
    participant Client
    participant Adapter as FileManager
    participant Page
    participant FileSystem as Local filesystem

    Client->>Adapter: write_page(page)
    Adapter->>Page: serialize()
    Page-->>Adapter: payload: bytes
    Adapter->>FileSystem: write(root/pages/page_id.bin, payload)
    FileSystem-->>Adapter: success
    Adapter-->>Client: True

    Client->>Adapter: load_page(page_id)
    Adapter->>FileSystem: read(root/pages/page_id.bin)
    FileSystem-->>Adapter: payload: bytes
    Adapter->>Page: deserialize(payload)
    Page-->>Adapter: Page
    Adapter-->>Client: Page
```

Paths that resolve outside `root_path` raise `StoragePathError`. Buffer Pool and Storage Engine will consume this `PageStoreProtocol` in later patterns.
