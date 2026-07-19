Nếu thiết kế theo chuẩn **enterprise DBMS** (PostgreSQL/SQL Server), thì **Unit Test không nên viết theo từng method**, mà theo **Business Capability** của từng Aggregate Root.

Với khoảng **40 core classes**, bạn sẽ có khoảng **800–1200 unit tests**.

Tôi sẽ liệt kê các **test suite** mà một DBMS thực sự cần có.

---

# 1. DatabaseServerTests

```text
StartServer_ShouldInitializeAllServices()

StopServer_ShouldShutdownGracefully()

RestartServer_ShouldRestartAllServices()

CreateDatabase_ShouldRegisterCatalog()

DropDatabase_ShouldRemoveMetadata()

OpenDatabase_ShouldLoadStorage()

CloseDatabase_ShouldFlushBuffers()

RecoverAfterCrash_ShouldReplayWAL()

RejectDuplicateDatabaseName()

ValidateConfigurationOnStartup()
```

---

# 2. DatabaseManagerTests

```text
CreateDatabase()

DropDatabase()

RenameDatabase()

AttachDatabase()

DetachDatabase()

BackupDatabase()

RestoreDatabase()

ListDatabases()

DatabaseExists()

ValidateDatabaseName()
```

---

# 3. DatabaseTests

```text
Open()

Close()

SetReadOnly()

ChangeRecoveryModel()

AddSchema()

RemoveSchema()

GrantAccess()

RevokeAccess()

CalculateDatabaseSize()

UpdateStatistics()
```

---

# 4. SchemaTests

```text
CreateTable()

DropTable()

RenameSchema()

MoveTable()

CreateView()

CreateProcedure()

CreateFunction()

CreateSequence()

ValidateDuplicateObjectName()
```

---

# 5. TableTests

```text
InsertRow()

UpdateRow()

DeleteRow()

Truncate()

AddColumn()

RemoveColumn()

RenameColumn()

AddConstraint()

DropConstraint()

CreateIndex()

DropIndex()

CreatePartition()

MovePartition()

Analyze()

Vacuum()

RebuildIndexes()

EnableCompression()

EnableEncryption()
```

---

# 6. ColumnTests

```text
ValidateNullable()

ValidateDataType()

ValidateLength()

ValidatePrecision()

ApplyDefaultValue()

GenerateIdentity()

EvaluateComputedColumn()

ApplyMasking()

EncryptColumn()

ChangeDataType()

RenameColumn()
```

---

# 7. RowTests

```text
CreateRow()

UpdateRow()

DeleteRow()

CloneVersion()

RestoreVersion()

CompareRows()

Serialize()

Deserialize()

CalculateRowSize()
```

---

# 8. ConstraintTests

```text
ValidatePrimaryKey()

ValidateUnique()

ValidateForeignKey()

ValidateCheckConstraint()

CascadeDelete()

CascadeUpdate()

RestrictDelete()

DisableConstraint()

EnableConstraint()
```

---

# 9. IndexTests

```text
CreateIndex()

DropIndex()

Search()

InsertKey()

DeleteKey()

SplitNode()

MergeNode()

Rebuild()

Reorganize()

EstimateSelectivity()

UpdateStatistics()
```

---

# 10. TransactionManagerTests

```text
BeginTransaction()

Commit()

Rollback()

RollbackToSavepoint()

NestedTransaction()

DistributedTransaction()

Timeout()

Cancel()

Retry()

RecoverTransaction()
```

---

# 11. TransactionTests

```text
CommitChanges()

RollbackChanges()

CreateSavepoint()

ReleaseSavepoint()

SetIsolationLevel()

ChangeState()

AcquireLock()

ReleaseLock()
```

---

# 12. LockManagerTests

```text
AcquireSharedLock()

AcquireExclusiveLock()

UpgradeLock()

DowngradeLock()

ReleaseLock()

DetectDeadlock()

TimeoutWaiting()

ReleaseAllLocks()
```

---

# 13. MVCCManagerTests

```text
CreateSnapshot()

ReadVisibleVersion()

SkipInvisibleVersion()

CreateVersion()

DeleteVersion()

GarbageCollect()

Vacuum()

MergeVersionChain()
```

---

# 14. BufferPoolTests

```text
PinPage()

UnpinPage()

EvictPage()

FlushPage()

ReplaceLRU()

ReplaceClock()

AllocateFrame()

ReleaseFrame()
```

---

# 15. StorageEngineTests

```text
AllocatePage()

ReadPage()

WritePage()

FreePage()

AllocateExtent()

ReleaseExtent()

SplitPage()

MergePage()

CompressPage()

EncryptPage()
```

---

# 16. WALManagerTests

```text
AppendLog()

FlushLog()

Checkpoint()

RotateLog()

ArchiveLog()

RecoverFromLog()

ValidateLSN()

ReplayRedo()
```

---

# 17. RecoveryManagerTests

```text
CrashRecovery()

Redo()

Undo()

RecoverCheckpoint()

RecoverCommitted()

RollbackIncomplete()

RecoverCorruptedLog()
```

---

# 18. SQLParserTests

```text
ParseSelect()

ParseInsert()

ParseUpdate()

ParseDelete()

ParseCreateTable()

ParseAlterTable()

ParseJoin()

ParseSubQuery()

ParseCTE()

ParseWindowFunction()

ParseInvalidSyntax()
```

---

# 19. QueryOptimizerTests

```text
OptimizeJoinOrder()

PredicatePushdown()

ConstantFolding()

ProjectionPruning()

ChooseIndex()

EstimateCost()

EstimateCardinality()

ChooseParallelPlan()

GeneratePhysicalPlan()
```

---

# 20. QueryExecutorTests

```text
ExecuteSelect()

ExecuteInsert()

ExecuteUpdate()

ExecuteDelete()

ExecuteJoin()

ExecuteAggregate()

ExecuteGroupBy()

ExecuteSort()

ExecuteParallel()

CancelExecution()
```

---

# 21. CatalogManagerTests

```text
RegisterObject()

RemoveObject()

LookupObject()

RefreshMetadata()

ResolveDependency()

UpdateStatistics()

CacheMetadata()
```

---

# 22. StatisticsManagerTests

```text
CollectStatistics()

UpdateHistogram()

EstimateCardinality()

EstimateDistinctValues()

RefreshStatistics()
```

---

# 23. SecurityManagerTests

```text
Authenticate()

Authorize()

GrantPermission()

RevokePermission()

ChangePassword()

LockUser()

UnlockUser()

AuditLogin()
```

---

# 24. UserTests

```text
CreateUser()

DisableUser()

EnableUser()

ResetPassword()

AssignRole()

RemoveRole()
```

---

# 25. RoleTests

```text
CreateRole()

DeleteRole()

GrantPermission()

RevokePermission()

AddMember()

RemoveMember()
```

---

# 26. ReplicationManagerTests

```text
StartReplication()

StopReplication()

ReplicateLog()

Failover()

PromoteReplica()

SynchronizeReplica()

Heartbeat()

ResolveSplitBrain()
```

---

# 27. BackupManagerTests

```text
FullBackup()

IncrementalBackup()

DifferentialBackup()

RestoreBackup()

VerifyBackup()

BackupCompression()
```

---

# 28. MonitoringManagerTests

```text
CollectMetrics()

DetectSlowQuery()

CaptureDeadlock()

CaptureBlocking()

RaiseAlert()

ExportMetrics()
```

---

# 29. ConfigurationManagerTests

```text
LoadConfiguration()

ReloadConfiguration()

ValidateConfiguration()

ApplyConfiguration()

RollbackConfiguration()
```

---

# 30. SessionManagerTests

```text
OpenSession()

CloseSession()

TimeoutSession()

AssociateTransaction()

DisconnectClient()
```

---

# 31. ConnectionPoolTests

```text
AcquireConnection()

ReleaseConnection()

ReuseConnection()

EvictIdleConnection()

DetectLeak()

MaxPoolSize()
```

---

# 32. PageTests

```text
InsertTuple()

DeleteTuple()

Split()

Merge()

CalculateChecksum()

Serialize()

Deserialize()
```

---

# 33. FileManagerTests

```text
CreateFile()

DeleteFile()

Read()

Write()

ExpandFile()

ShrinkFile()
```

---

# 34. DeadlockDetectorTests

```text
DetectCycle()

AbortVictim()

ReleaseLocks()

RetryTransaction()
```

---

# 35. BTreeIndexTests

```text
Insert()

Delete()

Search()

Split()

Merge()

BorrowFromSibling()

Rebalance()

RangeScan()
```

---

# 36. HashIndexTests

```text
Insert()

Delete()

Lookup()

SplitBucket()

Expand()
```

---

# 37. ClusterManagerTests

```text
JoinCluster()

LeaveCluster()

ElectLeader()

SynchronizeNodes()

Heartbeat()

RecoverNode()
```

---

# 38. ViewTests

```text
CreateView()

RefreshMaterializedView()

ResolveDependencies()

ValidateDefinition()
```

---

# 39. StoredProcedureTests

```text
Compile()

Execute()

CachePlan()

ValidateParameters()

HandleExceptions()
```

---

# 40. TriggerTests

```text
BeforeInsert()

AfterInsert()

BeforeUpdate()

AfterUpdate()

BeforeDelete()

AfterDelete()

DisableTrigger()

EnableTrigger()
```

# Tổng số lượng test

| Category                   |  Approx. Test Cases |
| -------------------------- | ------------------: |
| Metadata                   |                 120 |
| Storage                    |                 180 |
| Transactions               |                 150 |
| Query Processing           |                 180 |
| Security                   |                  70 |
| Replication & Recovery     |                 100 |
| Monitoring & Configuration |                  60 |
| **Total**                  | **≈860 Unit Tests** |

## Tiếp theo nên thiết kế Integration Tests

Đối với một DBMS, Unit Tests mới chỉ kiểm tra từng thành phần riêng lẻ. Giá trị lớn hơn đến từ **Integration Tests**, ví dụ:

* `Insert → Commit → WAL → Recovery → Verify Data`
* `Concurrent Update → LockManager → MVCC → Commit`
* `Create Table → Create Index → Insert Rows → Optimizer Uses Index`
* `Backup → Restore → Consistency Check`
* `Primary Node Commit → Replication → Replica Read`
* `Crash During Commit → Restart → Recovery → Data Integrity`

Một DBMS trưởng thành thường có số lượng **Integration Tests** ngang bằng hoặc nhiều hơn Unit Tests (khoảng 1.000–2.000 bài kiểm thử), vì phần lớn rủi ro nằm ở sự phối hợp giữa các subsystem hơn là ở từng lớp riêng lẻ.