# Storage Engine - Class Diagrams

## 1. Data Mapper (Record Read/Write)

`RecordMapper` is the Data Mapper: it converts the database-object `Row` into a storage `Record` and bytes without adding storage details to `Row`. `RecordManager` uses that mapper to place bytes in a `Page` slot.

```mermaid
classDiagram
    direction LR

    class Row {
        +row_id: str
        +values: list | dict
        +version: str
        +read() list | dict
        +update(new_values: list | dict) bool
    }

    class Record {
        +record_id: str | int
        +values: list | dict
        +version: str
        +serialize() bytes
        +deserialize(payload: bytes) Record
    }

    class RecordMapper {
        +to_record(row: Row) Record
        +to_row(record: Record) Row
        +serialize(row: Row) bytes
        +deserialize(payload: bytes) Row
    }

    class RecordManager {
        +page_manager: PageManager
        +mapper: RecordMapper
        +insert_row(row: Row) str
        +read_row(location: str) Row
        +update_row(location: str, row: Row) bool
        +delete_row(location: str) bool
    }

    class PageManager {
        +pages: dict[int, Page]
        +allocate_page() int
        +get_page(page_id: int) Page | None
        +release_page(page_id: int, deallocate: bool) bool
        +get_page_with_free_space(required_bytes: int) Page
    }

    class Page {
        +PAGE_SIZE: int
        +page_id: int
        +free_space: int
        +read_tuple(slot_id: int) bytes | None
        +insert_tuple(payload: bytes) int
        +write_tuple(slot_id: int, payload: bytes) bool
        +delete_tuple(slot_id: int) bool
    }

    RecordMapper ..> Row : maps to/from
    RecordMapper ..> Record : serializes
    RecordManager --> RecordMapper : uses
    RecordManager --> PageManager : uses
    PageManager *-- Page : owns
```

`PageManager` currently owns in-memory pages. File persistence and buffer-pool behavior are intentionally outside this pattern implementation.

---

## 2. Adapter (File Access)

`FileManager` adapts root-relative storage operations to the local filesystem. It also implements `PageStoreProtocol`, so a future buffer pool can load and flush `Page` objects without depending on filesystem details.

```mermaid
classDiagram
    direction LR

    class FileManager {
        +root_path: str
        +create_file(path: str) bool
        +read(path: str, offset: int, length: int | None) bytes
        +write(path: str, offset: int, data: bytes) bool
        +load_page(page_id: int) Page | None
        +write_page(page: Page) bool
    }

    class PageStoreProtocol {
        <<Protocol>>
        +load_page(page_id: int) Page | None
        +write_page(page: Page) bool
    }

    class Page {
        +page_id: int
        +serialize() bytes
        +deserialize(payload: bytes) Page
    }

    class Path {
        <<standard library>>
        +open(mode: str)
        +resolve() Path
    }

    FileManager ..|> PageStoreProtocol : implements
    FileManager ..> Page : serializes
    FileManager --> Path : adapts to
```

`FileManager` rejects paths outside `root_path`. It is not yet injected into `PageManager`, `BufferPool`, or `StorageEngine`.
