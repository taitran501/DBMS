from dataclasses import dataclass

class IndexAccessMethod:
    B_TREE = "B_TREE"; HASH = "HASH"

@dataclass(frozen=True)
class IndexDescriptor:
    name: str
    index_type: str
    columns: tuple[str, ...]
    unique: bool = False

@dataclass(frozen=True)
class IndexOrganization:
    access_method: str = IndexAccessMethod.B_TREE

class IndexMaintainer:
    def __init__(self): self.entries = {}
    def maintain_index_entry(self, index, key, row_id, op):
        ids = self.entries.setdefault(key, set()); operation = op.upper()
        if operation == "INSERT":
            if index.unique and ids and row_id not in ids: raise ValueError(f"Unique index {index.name} conflict for key {key}")
            ids.add(row_id)
        elif operation == "DELETE":
            ids.discard(row_id)
            if not ids: self.entries.pop(key, None)
        elif operation == "UPDATE": ids.add(row_id)
        else: raise ValueError(f"Unsupported index operation {op}")
    def find_row_ids_by_key(self, key): return tuple(sorted(self.entries.get(key, ())))
    def find_row_ids_by_range(self, start=None, end=None):
        result = []
        for key in sorted(self.entries):
            if (start is None or key >= start) and (end is None or key <= end): result.extend(sorted(self.entries[key]))
        return tuple(result)

class Index:
    def __init__(self, name, index_type=None, columns=None, unique=False, organization=None, maintainer=None):
        self.descriptor = name if isinstance(name, IndexDescriptor) else IndexDescriptor(name, index_type or "", tuple(columns or ()), unique)
        self.name = self.descriptor.name; self.index_type = self.descriptor.index_type; self.columns = list(self.descriptor.columns); self.unique = self.descriptor.unique
        self.organization = organization or IndexOrganization(self.index_type); self.maintainer = maintainer or IndexMaintainer()

class IndexManager:
    def __init__(self): self.indexes = {}
    def create_index(self, table_name, index):
        items = self.indexes.setdefault(table_name, [])
        if any(i.name == index.name for i in items): raise ValueError(f"Index {index.name} already exists on table {table_name}")
        items.append(index)
    def drop_index(self, table_name, index_name):
        if table_name in self.indexes: self.indexes[table_name] = [i for i in self.indexes[table_name] if i.name != index_name]
    def get_index(self, table_name, index_name):
        for index in self.indexes.get(table_name, []):
            if index.name == index_name: return index
        raise ValueError(f"Index {index_name} not found on table {table_name}")
    def maintain_table_indexes(self, table_name, values, row_id, operation):
        completed = []
        try:
            for index in self.indexes.get(table_name, []):
                key = tuple(values.get(c) for c in index.columns); index.maintainer.maintain_index_entry(index.descriptor, key, row_id, operation.upper()); completed.append((index, key))
        except Exception:
            inverse = "DELETE" if operation.upper() == "INSERT" else "INSERT"
            for index, key in reversed(completed): index.maintainer.maintain_index_entry(index.descriptor, key, row_id, inverse)
            raise
    def find_indexed_row_ids(self, table_name, index_name, key): return self.get_index(table_name, index_name).maintainer.find_row_ids_by_key(tuple(key))
    def find_indexed_row_ids_in_range(self, table_name, index_name, start=None, end=None):
        index = self.get_index(table_name, index_name)
        if index.index_type != IndexAccessMethod.B_TREE: raise ValueError("Range lookup requires B_TREE index")
        return index.maintainer.find_row_ids_by_range(tuple(start) if start is not None else None, tuple(end) if end is not None else None)
    def rebuild_index(self, table_name, index_name, rows):
        index = self.get_index(table_name, index_name)
        index.maintainer.entries.clear()
        for row_id, values in rows:
            key = tuple(values.get(column) for column in index.columns)
            index.maintainer.maintain_index_entry(index.descriptor, key, row_id, "INSERT")
    def rename_table(self, table_name, new_table_name):
        if table_name in self.indexes:
            self.indexes[new_table_name] = self.indexes.pop(table_name)
    def rename_column(self, table_name, column_name, new_name):
        for index in self.indexes.get(table_name, []):
            columns = tuple(new_name if column == column_name else column for column in index.columns)
            index.descriptor = IndexDescriptor(index.name, index.index_type, columns, index.unique)
            index.columns = list(columns)
