from typing import Union, Optional

class IndexDescriptor:
    def __init__(self, name: str, index_type: str, columns: list[str], unique: bool = False):
        self.name = name
        self.index_type = index_type  # e.g., B_TREE, HASH
        self.columns = columns
        self.unique = unique

class IndexAccessMethod:
    B_TREE = "B_TREE"
    HASH = "HASH"

class IndexOrganization:
    def __init__(self, access_method: str = IndexAccessMethod.B_TREE):
        self.access_method = access_method

class IndexMaintainer:
    def __init__(self):
        pass

    def maintain(self, index: IndexDescriptor, key: object, row_id: int, op: str) -> None:
        # op: INSERT, UPDATE, DELETE
        pass

class Index:
    def __init__(self, name: Union[str, IndexDescriptor], index_type: Optional[str] = None, columns: Optional[list[str]] = None, unique: bool = False, organization: Optional[IndexOrganization] = None, maintainer: Optional[IndexMaintainer] = None):
        if isinstance(name, IndexDescriptor):
            self.descriptor = name
        else:
            self.descriptor = IndexDescriptor(name, index_type or "", columns or [], unique)
        
        self.name = self.descriptor.name
        self.index_type = self.descriptor.index_type
        self.columns = self.descriptor.columns
        self.unique = self.descriptor.unique
        self.organization = organization or IndexOrganization(self.index_type)
        self.maintainer = maintainer or IndexMaintainer()

class IndexManager:
    def __init__(self):
        # table_name -> list of Index objects
        self.indexes: dict[str, list[Index]] = {}

    def create_index(self, table_name: str, index: Index) -> None:
        if table_name not in self.indexes:
            self.indexes[table_name] = []
        if any(idx.name == index.name for idx in self.indexes[table_name]):
            raise ValueError(f"Index {index.name} already exists on table {table_name}")
        self.indexes[table_name].append(index)

    def drop_index(self, table_name: str, index_name: str) -> None:
        if table_name in self.indexes:
            self.indexes[table_name] = [idx for idx in self.indexes[table_name] if idx.name != index_name]

    def get_index(self, table_name: str, index_name: str) -> Index:
        if table_name in self.indexes:
            for idx in self.indexes[table_name]:
                if idx.name == index_name:
                    return idx
        raise ValueError(f"Index {index_name} not found on table {table_name}")

    def maintain_table_indexes(self, table_name: str, values: dict, row_id: int, operation: str) -> None:
        for index in self.indexes.get(table_name, []):
            key = tuple(values.get(column) for column in index.columns)
            index.maintainer.maintain(index.descriptor, key, row_id, operation.upper())
