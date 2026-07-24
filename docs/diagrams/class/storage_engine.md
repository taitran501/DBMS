# Storage Engine - Class Diagrams

## 1. Data Mapper (Record Read/Write)

`RecordMapper` is the Data Mapper: it converts the database-object `Row` into a storage `Record` and bytes without adding storage details to `Row`. `RecordManager` uses that mapper to place bytes in a `Page` slot.

```mermaid
classDiagram
    direction TB

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
    direction TB

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

`FileManager` rejects paths outside `root_path`. It is used by `BufferPool` through `PageStoreProtocol`; `PageManager` and `StorageEngine` are not yet connected to it.

---

## 3. Proxy (Page Loading)

`BufferPool` is a cache proxy for `PageStoreProtocol`. It returns an in-memory page when one is cached; otherwise it loads the page through the store, caches it, and pins it for the caller.

```mermaid
classDiagram
    direction TB

    class BufferPool {
        +capacity: int
        +page_store: PageStoreProtocol
        +pages: dict[int, Page]
        +pin_counts: dict[int, int]
        +dirty_page_ids: set[int]
        +pin_page(page_id: int) Page | None
        +unpin_page(page_id: int) bool
        +cache_page(page: Page) bool
        +flush_page(page_id: int) bool
        +flush_all_pages() bool
    }

    class PageStoreProtocol {
        <<Protocol>>
        +load_page(page_id: int) Page | None
        +write_page(page: Page) bool
    }

    class FileManager {
        +load_page(page_id: int) Page | None
        +write_page(page: Page) bool
    }

    class Page

    BufferPool --> PageStoreProtocol : loads and flushes
    FileManager ..|> PageStoreProtocol : implements
    BufferPool o-- Page : caches
```

`pin_page()` returns `None` when the store has no page with the requested id. Buffer-pool state remains in memory; `FileManager` owns persisted page bytes.

---

## 4. Strategy (Buffer Replacement)

`BufferPool` delegates victim selection to an injected `BufferReplacementStrategy`. It still decides which pages are eligible: only unpinned pages can be evicted.

```mermaid
classDiagram
    direction TB

    class BufferPool {
        +replacement_strategy: BufferReplacementStrategy
        +cache_page(page: Page) bool
        +evict_page() bool
    }

    class BufferReplacementStrategy {
        <<abstract>>
        +record_page(page_id: int) None
        +record_access(page_id: int) None
        +remove_page(page_id: int) None
        +select_victim(candidate_page_ids: Collection) int | None
    }

    class FifoReplacementStrategy {
        +select_victim(candidate_page_ids: Collection) int | None
    }

    class LruReplacementStrategy {
        +record_access(page_id: int) None
        +select_victim(candidate_page_ids: Collection) int | None
    }

    BufferPool --> BufferReplacementStrategy : delegates selection to
    FifoReplacementStrategy --|> BufferReplacementStrategy
    LruReplacementStrategy --|> BufferReplacementStrategy
```

FIFO is the default. LRU demonstrates that callers can replace the algorithm without changing `BufferPool`.
