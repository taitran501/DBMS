class Index:
    def __init__(
        self,
        index_id: str = "",
        name: str = "",
        index_type: str = "",
        unique: bool = False,
        entries: dict[object, list[str]] | None = None,
        columns: list[str] | tuple[str, ...] | None = None,
    ) -> None:
        self.index_id = index_id
        self.name = name
        self.type = index_type
        self.unique = unique
        self.entries = {} if entries is None else entries
        self.columns = tuple(columns or ())

    def search(self, key: object) -> list:
        return list(self.entries.get(key, []))

    def insert_key(self, key: object, row_id: str) -> bool:
        row_ids = self.entries.setdefault(key, [])
        if row_id in row_ids or (self.unique and row_ids):
            return False
        row_ids.append(row_id)
        return True

    def delete_key(self, key: object, row_id: str) -> bool:
        row_ids = self.entries.get(key)
        if row_ids is None or row_id not in row_ids:
            return False

        row_ids.remove(row_id)
        if not row_ids:
            del self.entries[key]
        return True


class BTreeIndex(Index):
    """Index product created by :class:`BTreeIndexFactory`."""

    def __init__(
        self,
        index_id: str = "",
        name: str = "",
        columns: list[str] | tuple[str, ...] | None = None,
        unique: bool = False,
        entries: dict[object, list[str]] | None = None,
    ) -> None:
        super().__init__(index_id, name, "BTree", unique, entries, columns)


class HashIndex(Index):
    """Index product created by :class:`HashIndexFactory`."""

    def __init__(
        self,
        index_id: str = "",
        name: str = "",
        columns: list[str] | tuple[str, ...] | None = None,
        unique: bool = False,
        entries: dict[object, list[str]] | None = None,
    ) -> None:
        super().__init__(index_id, name, "Hash", unique, entries, columns)
