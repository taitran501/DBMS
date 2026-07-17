# Storage Engine Unit Test Sequences

This document outlines the detailed sequence diagrams for the unit tests in the `Storage Engine` subsystem.

---

## 1. test_buffer_pool.py

```mermaid
sequenceDiagram
    autonumber
    participant Test as test_buffer_pool.py
    participant SUT as BufferPool
    participant Page as Page

    Note over Test: test_buffer_pool_can_be_created
    Test->>SUT: BufferPool(10)
    SUT-->>Test: pool
    Test->>Test: assert isinstance(pool, BufferPool)

    Note over Test: test_pin_page
    Test->>SUT: pin_page(1)
    activate SUT
    SUT->>SUT: increment_pin_count(1)
    SUT-->>Test: Page
    deactivate SUT

    Note over Test: test_cache_page
    Test->>SUT: cache_page(Page)
    activate SUT
    SUT->>SUT: store_in_hashmap(Page.page_id, Page)
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_get_cached_page
    Test->>SUT: get_cached_page(1)
    activate SUT
    SUT->>SUT: lookup_hashmap(1)
    SUT-->>Test: Page
    deactivate SUT

    Note over Test: test_load_missing_page
    Test->>SUT: pin_page(5)
    activate SUT
    SUT->>SUT: lookup_hashmap(5)
    SUT-->>SUT: None (Cache Miss)
    SUT->>StorageEngine: read_page(5)
    StorageEngine-->>SUT: Page
    SUT->>SUT: store_in_hashmap(5, Page)
    SUT-->>Test: Page
    deactivate SUT

    Note over Test: test_enforce_capacity
    Test->>SUT: cache_page(new_page)
    activate SUT
    SUT->>SUT: check_capacity()
    SUT-->>SUT: capacity_exceeded
    SUT->>SUT: evict_page()
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_evict_page
    Test->>SUT: evict_page()
    activate SUT
    SUT->>SUT: select_unpinned_lru_page()
    SUT->>StorageEngine: write_page(evicted_page)
    SUT->>SUT: remove_from_hashmap(evicted_page.page_id)
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_preserve_pinned_page
    Test->>SUT: evict_page()
    activate SUT
    SUT->>SUT: find_candidate_pages()
    Note over SUT: Skip pages with pin_count > 0
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_mark_dirty
    Test->>SUT: mark_dirty(1)
    activate SUT
    SUT->>SUT: set_dirty_flag(1, True)
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_flush_page
    Test->>SUT: flush_page(1)
    activate SUT
    SUT->>StorageEngine: write_page(Page)
    SUT->>SUT: set_dirty_flag(1, False)
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_flush_all_pages
    Test->>SUT: flush_all_pages()
    activate SUT
    SUT->>SUT: get_all_dirty_pages()
    SUT->>StorageEngine: write_page(dirty_page1)
    SUT->>StorageEngine: write_page(dirty_page2)
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_buffer_pool_stores_capacity
    Test->>SUT: BufferPool(10)
    SUT-->>Test: pool
    Test->>Test: assert pool.capacity == 10
```

---

## 2. test_file_manager.py

```mermaid
sequenceDiagram
    autonumber
    participant Test as test_file_manager.py
    participant SUT as FileManager

    Note over Test: test_file_manager_can_be_created
    Test->>SUT: FileManager("/data")
    SUT-->>Test: fm
    Test->>Test: assert isinstance(fm, FileManager)

    Note over Test: test_create_file
    Test->>SUT: create_file("db.dat")
    activate SUT
    SUT->>SUT: open_os_file_handle("db.dat", write=True)
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_read_file_bytes
    Test->>SUT: read("db.dat", offset=0, length=4096)
    activate SUT
    SUT->>SUT: read_from_disk("db.dat", 0, 4096)
    SUT-->>Test: b"page_data"
    deactivate SUT

    Note over Test: test_write
    Test->>SUT: write("db.dat", offset=0, b"new_data")
    activate SUT
    SUT->>SUT: write_to_disk("db.dat", 0, b"new_data")
    SUT-->>Test: True
    deactivate SUT
```

---

## 3. test_log_file_manager.py

```mermaid
sequenceDiagram
    autonumber
    participant Test as test_log_file_manager.py
    participant SUT as LogFileManager

    Note over Test: test_append_log_entry
    Test->>SUT: append_log_entry(b"log_data")
    activate SUT
    SUT->>SUT: calculate_checksum(b"log_data")
    SUT->>SUT: format_log_record()
    SUT->>SUT: append_to_buffer()
    SUT-->>Test: lsn
    deactivate SUT

    Note over Test: test_read_log_entry
    Test->>SUT: read_log_entry(lsn)
    activate SUT
    SUT->>SUT: seek_to_lsn(lsn)
    SUT->>SUT: read_formatted_record()
    SUT-->>Test: b"log_data"
    deactivate SUT

    Note over Test: test_read_log_range
    Test->>SUT: read_log_range(start_lsn, end_lsn)
    activate SUT
    SUT->>SUT: read_all_records_between(start_lsn, end_lsn)
    SUT-->>Test: [entry1, entry2]
    deactivate SUT

    Note over Test: test_detect_corrupted_entry
    Test->>SUT: read_log_entry(corrupted_lsn)
    activate SUT
    SUT->>SUT: read_formatted_record()
    SUT->>SUT: verify_checksum()
    SUT-->>SUT: checksum_mismatch
    SUT-->>Test: raises LogCorruptException
    deactivate SUT

    Note over Test: test_flush_log
    Test->>SUT: flush_log()
    activate SUT
    SUT->>SUT: write_buffer_to_disk()
    SUT->>SUT: fsync()
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_truncate_log
    Test->>SUT: truncate_log(lsn)
    activate SUT
    SUT->>SUT: discard_logs_before(lsn)
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_assign_sequence_number
    Test->>SUT: append_log_entry(b"log")
    activate SUT
    SUT->>SUT: get_next_lsn()
    SUT-->>Test: lsn
    deactivate SUT

    Note over Test: test_log_file_manager_can_be_created
    Test->>SUT: LogFileManager()
    SUT-->>Test: manager
    Test->>Test: assert isinstance(manager, LogFileManager)
```

---

## 4. test_page.py

```mermaid
sequenceDiagram
    autonumber
    participant Test as test_page.py
    participant SUT as Page

    Note over Test: test_page_can_be_created
    Test->>SUT: Page(1, b"initial_data")
    SUT-->>Test: page
    Test->>Test: assert page.page_id == 1
    Test->>Test: assert page.data == b"initial_data"

    Note over Test: test_read_tuple
    Test->>SUT: page.read_tuple(slot_offset=10)
    activate SUT
    SUT->>SUT: parse_slot_header(10)
    SUT-->>Test: tuple_bytes
    deactivate SUT

    Note over Test: test_write_tuple
    Test->>SUT: page.write_tuple(slot_offset=10, b"tuple_data")
    activate SUT
    SUT->>SUT: write_slot_header(10)
    SUT->>SUT: write_bytes(b"tuple_data")
    SUT-->>Test: True
    deactivate SUT
```

---

## 5. test_page_manager.py

```mermaid
sequenceDiagram
    autonumber
    participant Test as test_page_manager.py
    participant SUT as PageManager

    Note over Test: test_allocate_page
    Test->>SUT: allocate_page()
    activate SUT
    SUT->>SUT: pop_free_list()
    SUT-->>SUT: None (No Free Pages)
    SUT->>SUT: extend_database_file()
    SUT-->>Test: new_page_id
    deactivate SUT

    Note over Test: test_get_page
    Test->>SUT: get_page(2)
    activate SUT
    SUT->>BufferPool: pin_page(2)
    BufferPool-->>SUT: Page
    SUT-->>Test: Page
    deactivate SUT

    Note over Test: test_release_page
    Test->>SUT: release_page(2)
    activate SUT
    SUT->>BufferPool: unpin_page(2)
    BufferPool-->>SUT: True
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_reuse_page
    Test->>SUT: release_page(2, deallocate=True)
    activate SUT
    SUT->>SUT: push_free_list(2)
    SUT-->>Test: True
    deactivate SUT
    Test->>SUT: allocate_page()
    activate SUT
    SUT->>SUT: pop_free_list()
    SUT-->>Test: 2
    deactivate SUT

    Note over Test: test_track_page_free_space
    Test->>SUT: track_page_free_space(2)
    activate SUT
    SUT->>SUT: read_page_header_free_space(2)
    SUT-->>Test: free_space_bytes
    deactivate SUT

    Note over Test: test_reject_full_page
    Test->>SUT: get_page_with_free_space(required_bytes=2048)
    activate SUT
    SUT->>SUT: scan_page_space_directory(required_bytes=2048)
    SUT-->>Test: raises StorageFullException
    deactivate SUT

    Note over Test: test_page_manager_can_be_created
    Test->>SUT: PageManager()
    SUT-->>Test: manager
    Test->>Test: assert isinstance(manager, PageManager)
```

---

## 6. test_record.py

```mermaid
sequenceDiagram
    autonumber
    participant Test as test_record.py
    participant SUT as Record

    Note over Test: test_serialize_record
    Test->>SUT: Record(1, {"name": "Ada"}).serialize()
    activate SUT
    SUT->>SUT: convert_values_to_bytes()
    SUT-->>Test: b"serialized_bytes"
    deactivate SUT

    Note over Test: test_deserialize_record
    Test->>SUT: Record.deserialize(b"serialized_bytes")
    activate SUT
    SUT->>SUT: parse_bytes_to_values()
    SUT-->>Test: Record(1, {"name": "Ada"})
    deactivate SUT

    Note over Test: test_record_stores_identifier_and_values
    Test->>SUT: Record(1, {"name": "Ada"})
    SUT-->>Test: record
    Test->>Test: assert record.record_id == 1
    Test->>Test: assert record.values == {"name": "Ada"}
```

---

## 7. test_record_manager.py

```mermaid
sequenceDiagram
    autonumber
    participant Test as test_record_manager.py
    participant SUT as RecordManager
    participant Page as Page

    Note over Test: test_read_record
    Test->>SUT: read_record("rid1")
    activate SUT
    SUT->>SUT: parse_rid("rid1")
    SUT->>PageManager: get_page(page_id)
    PageManager-->>SUT: Page
    SUT->>Page: read_tuple(slot_id)
    Page-->>SUT: record_bytes
    SUT->>Record: deserialize(record_bytes)
    Record-->>SUT: record
    SUT-->>Test: record
    deactivate SUT

    Note over Test: test_move_record
    Test->>SUT: move_record("rid1", "rid2")
    activate SUT
    SUT->>SUT: delete_record("rid1")
    SUT->>SUT: insert_record_at_specific_id("rid2", record)
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_insert_record
    Test->>SUT: insert_record(record)
    activate SUT
    SUT->>PageManager: get_page_with_free_space(record.size)
    PageManager-->>SUT: Page
    SUT->>Record: serialize()
    Record-->>SUT: record_bytes
    SUT->>Page: write_tuple(record_bytes)
    Page-->>SUT: slot_id
    SUT-->>Test: rid(page_id, slot_id)
    deactivate SUT

    Note over Test: test_update_record
    Test->>SUT: update_record("rid1", updated_record)
    activate SUT
    SUT->>PageManager: get_page(page_id)
    PageManager-->>SUT: Page
    SUT->>Page: write_tuple(slot_id, updated_record.serialize())
    Page-->>SUT: True
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_delete_record
    Test->>SUT: delete_record("rid1")
    activate SUT
    SUT->>PageManager: get_page(page_id)
    PageManager-->>SUT: Page
    SUT->>Page: delete_tuple(slot_id)
    Page-->>SUT: True
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_reject_oversized_record
    Test->>SUT: insert_record(oversized_record)
    activate SUT
    SUT-->>Test: raises RecordOversizedException
    deactivate SUT

    Note over Test: test_record_manager_can_be_created
    Test->>SUT: RecordManager()
    SUT-->>Test: manager
    Test->>Test: assert isinstance(manager, RecordManager)
```

---

## 8. test_storage_allocator.py

```mermaid
sequenceDiagram
    autonumber
    participant Test as test_storage_allocator.py
    participant SUT as StorageAllocator

    Note over Test: test_allocate_storage_space
    Test->>SUT: allocate_space(1024)
    activate SUT
    SUT->>SUT: find_free_extent(1024)
    SUT->>SUT: mark_extent_allocated(extent)
    SUT-->>Test: extent_address
    deactivate SUT

    Note over Test: test_release_storage_space
    Test->>SUT: release_space(extent_address)
    activate SUT
    SUT->>SUT: mark_extent_free(extent_address)
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_reallocate_space
    Test->>SUT: reallocate_space(extent_address, 2048)
    activate SUT
    SUT->>SUT: release_space(extent_address)
    SUT->>SUT: allocate_space(2048)
    SUT-->>Test: new_extent_address
    deactivate SUT

    Note over Test: test_track_allocator_free_space
    Test->>SUT: get_free_space()
    activate SUT
    SUT->>SUT: sum_free_extents()
    SUT-->>Test: free_bytes
    deactivate SUT

    Note over Test: test_reject_exhausted_storage
    Test->>SUT: allocate_space(large_size)
    activate SUT
    SUT->>SUT: find_free_extent(large_size)
    SUT-->>SUT: None
    SUT-->>Test: raises OutOfStorageException
    deactivate SUT

    Note over Test: test_reject_double_release
    Test->>SUT: release_space(extent_address)
    activate SUT
    SUT->>SUT: is_already_free(extent_address)
    SUT-->>SUT: True
    SUT-->>Test: raises DoubleReleaseException
    deactivate SUT

    Note over Test: test_storage_allocator_can_be_created
    Test->>SUT: StorageAllocator()
    SUT-->>Test: allocator
    Test->>Test: assert isinstance(allocator, StorageAllocator)
```

---

## 9. test_storage_engine.py

```mermaid
sequenceDiagram
    autonumber
    participant Test as test_storage_engine.py
    participant Pool as BufferPool
    participant SUT as StorageEngine

    Note over Test: test_storage_engine_can_be_created
    Test->>SUT: StorageEngine(Pool)
    SUT-->>Test: engine
    Test->>Test: assert isinstance(engine, StorageEngine)

    Note over Test: test_initialize
    Test->>SUT: initialize()
    activate SUT
    SUT->>FileManager: create_file("db.dat")
    FileManager-->>SUT: True
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_read_page
    Test->>SUT: read_page(1)
    activate SUT
    SUT->>Pool: pin_page(1)
    Pool-->>SUT: Page
    SUT-->>Test: Page
    deactivate SUT

    Note over Test: test_write_page
    Test->>SUT: write_page(Page)
    activate SUT
    SUT->>Pool: mark_dirty(Page.page_id)
    SUT->>Pool: flush_page(Page.page_id)
    Pool-->>SUT: True
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_storage_engine_stores_buffer_pool
    Test->>Pool: BufferPool(16)
    Pool-->>Test: pool
    Test->>SUT: StorageEngine(pool)
    SUT-->>Test: engine
    Test->>Test: assert engine.buffer_pool is pool
```
