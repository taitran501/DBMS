# Transaction Unit Test Sequences

This document outlines the detailed sequence diagrams for the unit tests in the `Transaction` subsystem.

---

## 1. test_deadlock_manager.py

```mermaid
sequenceDiagram
    autonumber
    participant Test as test_deadlock_manager.py
    participant SUT as DeadlockManager

    Note over Test: test_build_wait_graph
    Test->>SUT: build_wait_graph(active_locks)
    activate SUT
    SUT->>SUT: add_nodes_and_dependency_edges()
    SUT-->>Test: wait_graph
    deactivate SUT

    Note over Test: test_detect_cycle
    Test->>SUT: detect_cycle(wait_graph)
    activate SUT
    SUT->>SUT: run_dfs_cycle_detection()
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_select_victim
    Test->>SUT: select_victim(cycle)
    activate SUT
    SUT->>SUT: compare_transaction_priorities()
    SUT-->>Test: victim_tx
    deactivate SUT

    Note over Test: test_abort_victim
    Test->>SUT: abort_victim(victim_tx)
    activate SUT
    SUT->>victim_tx: rollback()
    victim_tx-->>SUT: True
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_release_victim_locks
    Test->>SUT: release_victim_locks(victim_tx)
    activate SUT
    SUT->>LockManager: release_all(victim_tx)
    LockManager-->>SUT: True
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_retry_transaction
    Test->>SUT: retry_transaction(victim_tx)
    activate SUT
    SUT->>TransactionManager: begin_transaction()
    TransactionManager-->>SUT: new_tx
    SUT-->>Test: new_tx
    deactivate SUT

    Note over Test: test_deadlock_manager_can_be_created
    Test->>SUT: DeadlockManager()
    SUT-->>Test: manager
    Test->>Test: assert isinstance(manager, DeadlockManager)
```

---

## 2. test_isolation_manager.py

```mermaid
sequenceDiagram
    autonumber
    participant Test as test_isolation_manager.py
    participant SUT as IsolationManager

    Note over Test: test_read_committed
    Test->>SUT: enforce_read_committed(tx, row)
    activate SUT
    SUT->>SUT: check_committed_version(row)
    SUT-->>Test: visible_row
    deactivate SUT

    Note over Test: test_repeatable_read
    Test->>SUT: enforce_repeatable_read(tx, row)
    activate SUT
    SUT->>SUT: check_snapshot_version(tx, row)
    SUT-->>Test: visible_row
    deactivate SUT

    Note over Test: test_serializable
    Test->>SUT: enforce_serializable(tx, resource)
    activate SUT
    SUT->>LockManager: acquire_range_lock(tx, resource)
    LockManager-->>SUT: True
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_snapshot_isolation
    Test->>SUT: enforce_snapshot_isolation(tx, row)
    activate SUT
    SUT->>SUT: check_tx_snapshot(tx, row)
    SUT-->>Test: visible_row
    deactivate SUT

    Note over Test: test_prevent_dirty_read
    Test->>SUT: read_value(tx, uncommitted_row)
    activate SUT
    SUT->>SUT: filter_uncommitted()
    SUT-->>Test: None
    deactivate SUT

    Note over Test: test_prevent_nonrepeatable_read
    Test->>SUT: read_value(tx, modified_row)
    activate SUT
    SUT->>SUT: retrieve_initial_version(tx)
    SUT-->>Test: initial_row
    deactivate SUT

    Note over Test: test_prevent_phantom_read
    Test->>SUT: range_query(tx, range)
    activate SUT
    SUT->>SUT: filter_newly_inserted_rows(tx)
    SUT-->>Test: initial_range_rows
    deactivate SUT

    Note over Test: test_isolation_manager_can_be_created
    Test->>SUT: IsolationManager()
    SUT-->>Test: manager
    Test->>Test: assert isinstance(manager, IsolationManager)
```

---

## 3. test_lock_manager.py

```mermaid
sequenceDiagram
    autonumber
    participant Test as test_lock_manager.py
    participant SUT as LockManager

    Note over Test: test_acquire_lock
    Test->>SUT: acquire_lock(tx, "row1", "SHARED")
    activate SUT
    SUT->>SUT: check_compatibility("row1", "SHARED")
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_acquire_shared_lock
    Test->>SUT: acquire_lock(tx, "row1", "SHARED")
    SUT-->>Test: True

    Note over Test: test_acquire_exclusive_lock
    Test->>SUT: acquire_lock(tx, "row1", "EXCLUSIVE")
    SUT-->>Test: True

    Note over Test: test_upgrade_lock
    Test->>SUT: upgrade_lock(tx, "row1", "EXCLUSIVE")
    activate SUT
    SUT->>SUT: check_sole_holder(tx, "row1")
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_downgrade_lock
    Test->>SUT: downgrade_lock(tx, "row1", "SHARED")
    activate SUT
    SUT->>SUT: set_lock_mode("row1", "SHARED")
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_release_lock
    Test->>SUT: release_lock(tx, "row1")
    activate SUT
    SUT->>SUT: remove_holder(tx, "row1")
    SUT->>SUT: notify_waiters("row1")
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_detect_deadlock
    Test->>SUT: acquire_lock(tx1, "row2", "EXCLUSIVE")
    activate SUT
    SUT->>DeadlockManager: detect_cycle(wait_graph)
    DeadlockManager-->>SUT: True
    SUT-->>Test: raises DeadlockException
    deactivate SUT

    Note over Test: test_timeout_waiting
    Test->>SUT: acquire_lock(tx, "row1", "EXCLUSIVE", timeout=1)
    activate SUT
    SUT->>SUT: wait_for_lock("row1", timeout=1)
    SUT-->>Test: raises LockTimeoutException
    deactivate SUT

    Note over Test: test_release_all_locks
    Test->>SUT: release_all_locks(tx)
    activate SUT
    SUT->>SUT: find_all_locks_held_by(tx)
    SUT->>SUT: release_each_lock()
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_lock_manager_can_be_created
    Test->>SUT: LockManager()
    SUT-->>Test: manager
    Test->>Test: assert isinstance(manager, LockManager)
```

---

## 4. test_mvcc_manager.py

```mermaid
sequenceDiagram
    autonumber
    participant Test as test_mvcc_manager.py
    participant SUT as MVCCManager

    Note over Test: test_mvcc_manager_can_be_created
    Test->>SUT: MVCCManager({"row1": []})
    SUT-->>Test: mvcc
    Test->>Test: assert mvcc.version_chain_map == {"row1": []}

    Note over Test: test_create_snapshot
    Test->>SUT: MVCCManager({"row1": []})
    SUT-->>Test: mvcc
    Test->>SUT: mvcc.create_snapshot()
    SUT-->>Test: None
    Test->>Test: assert result is None

    Note over Test: test_read_visible_version
    Test->>SUT: MVCCManager({"row1": []})
    SUT-->>Test: mvcc
    Test->>SUT: mvcc.read_visible_version(row, tx)
    SUT-->>Test: row
    Test->>Test: assert result is row
```

---

## 5. test_transaction.py

```mermaid
sequenceDiagram
    autonumber
    participant Test as test_transaction.py
    participant SUT as Transaction

    Note over Test: test_create_savepoint
    Test->>SUT: create_savepoint("sp1")
    activate SUT
    SUT->>SUT: savepoints.append("sp1")
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_release_savepoint
    Test->>SUT: release_savepoint("sp1")
    activate SUT
    SUT->>SUT: savepoints.remove("sp1")
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_set_isolation_level
    Test->>SUT: set_isolation_level("SERIALIZABLE")
    activate SUT
    SUT->>SUT: set_level("SERIALIZABLE")
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_change_state
    Test->>SUT: change_state(TransactionStatus.COMMITTED)
    activate SUT
    SUT->>SUT: set_status(TransactionStatus.COMMITTED)
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_transaction_can_be_created
    Test->>SUT: Transaction(1, TransactionStatus.ACTIVE)
    SUT-->>Test: transaction
    Test->>Test: assert transaction.transaction_id == 1
    Test->>Test: assert transaction.status is TransactionStatus.ACTIVE
```

---

## 6. test_transaction_manager.py

```mermaid
sequenceDiagram
    autonumber
    participant Test as test_transaction_manager.py
    participant SUT as TransactionManager
    participant TX as Transaction

    Note over Test: test_transaction_manager_can_be_created
    Test->>SUT: TransactionManager()
    SUT-->>Test: manager

    Note over Test: test_begin_transaction
    Test->>SUT: begin_transaction()
    activate SUT
    SUT->>TX: Instantiate(new_id, ACTIVE)
    TX-->>SUT: tx
    SUT->>SUT: active_transactions[tx.id] = tx
    SUT-->>Test: tx
    deactivate SUT

    Note over Test: test_commit
    Test->>SUT: commit(tx)
    activate SUT
    SUT->>TX: change_state(COMMITTED)
    SUT->>LockManager: release_all_locks(tx)
    SUT->>SUT: remove_from_active(tx)
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_rollback
    Test->>SUT: rollback(tx)
    activate SUT
    SUT->>TX: change_state(ROLLED_BACK)
    SUT->>LockManager: release_all_locks(tx)
    SUT->>SUT: remove_from_active(tx)
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_rollback_to_savepoint
    Test->>SUT: rollback_to_savepoint(tx, "sp1")
    activate SUT
    SUT->>TX: rollback_changes_since("sp1")
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_nested_transaction
    Test->>SUT: begin_nested_transaction(parent_tx)
    activate SUT
    SUT->>TX: Instantiate_nested(new_id, parent_tx)
    TX-->>SUT: nested_tx
    SUT-->>Test: nested_tx
    deactivate SUT

    Note over Test: test_distributed_transaction
    Test->>SUT: prepare_distributed(tx)
    activate SUT
    SUT->>SUT: run_two_phase_commit_prepare(tx)
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_timeout
    Test->>SUT: begin_transaction(timeout=2)
    activate SUT
    SUT->>TX: Instantiate(new_id, ACTIVE)
    TX-->>SUT: tx
    SUT->>SUT: schedule_timeout_check(tx, timeout=2)
    SUT-->>Test: tx
    deactivate SUT

    Note over Test: test_cancel
    Test->>SUT: cancel(tx)
    activate SUT
    SUT->>SUT: rollback(tx)
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_retry
    Test->>SUT: retry(tx)
    activate SUT
    SUT->>SUT: rollback(tx)
    SUT->>SUT: begin_transaction()
    SUT-->>Test: new_tx
    deactivate SUT

    Note over Test: test_recover_transaction
    Test->>SUT: recover_transactions()
    activate SUT
    SUT->>WALManager: scan_active_records()
    WALManager-->>SUT: active_txs
    SUT->>SUT: resolve_uncommitted_txs(active_txs)
    SUT-->>Test: True
    deactivate SUT

    Note over Test: test_transaction_manager_returns_lifecycle_placeholders
    Test->>SUT: TransactionManager()
    SUT-->>Test: manager
    Test->>SUT: manager.begin_transaction()
    SUT-->>Test: None
    Test->>Test: assert result is None
    Test->>SUT: manager.commit(tx)
    SUT-->>Test: True
    Test->>Test: assert result is True
    Test->>SUT: manager.rollback(tx)
    SUT-->>Test: True
    Test->>Test: assert result is True
```

---

## 7. test_transaction_status.py

```mermaid
sequenceDiagram
    autonumber
    participant Test as test_transaction_status.py
    participant SUT as TransactionStatus

    Note over Test: test_transaction_status_defines_core_lifecycle_states
    Test->>Test: assert TransactionStatus.ACTIVE.name == "ACTIVE"
    Test->>Test: assert TransactionStatus.COMMITTED.name == "COMMITTED"
    Test->>Test: assert TransactionStatus.ROLLED_BACK.name == "ROLLED_BACK"
```
