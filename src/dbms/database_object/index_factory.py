from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from dbms.database_object.index import BTreeIndex, HashIndex, Index


class IndexFactory(ABC):
    """Creator interface for constructing a concrete Index product."""

    @abstractmethod
    def create_index(
        self,
        index_id: str,
        name: str,
        *,
        columns: Sequence[str] = (),
        unique: bool = False,
    ) -> Index:
        """Create the concrete index selected by this factory."""


class BTreeIndexFactory(IndexFactory):
    """Concrete creator for B-tree indexes."""

    def create_index(
        self,
        index_id: str,
        name: str,
        *,
        columns: Sequence[str] = (),
        unique: bool = False,
    ) -> BTreeIndex:
        return BTreeIndex(index_id, name, list(columns), unique)


class HashIndexFactory(IndexFactory):
    """Concrete creator for hash indexes."""

    def create_index(
        self,
        index_id: str,
        name: str,
        *,
        columns: Sequence[str] = (),
        unique: bool = False,
    ) -> HashIndex:
        return HashIndex(index_id, name, list(columns), unique)
