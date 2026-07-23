from pathlib import Path

from dbms.storage_engine.exceptions import StoragePathError
from dbms.storage_engine.page import Page


class FileManager:
    """Adapts safe, root-relative DBMS file operations to the local filesystem."""

    _PAGE_DIRECTORY = "pages"

    def __init__(self, root_path: str = "") -> None:
        self._root_path = Path(root_path or ".").resolve()
        self._root_path.mkdir(parents=True, exist_ok=True)
        self.root_path = str(self._root_path)

    def create_file(self, path: str) -> bool:
        target = self._resolve_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.touch(exist_ok=True)
        return True

    def read(
        self,
        path: str,
        *,
        offset: int = 0,
        length: int | None = None,
    ) -> bytes:
        self._validate_range(offset, length)
        with self._resolve_path(path).open("rb") as data_file:
            data_file.seek(offset)
            return data_file.read(length)

    def write(self, path: str, *, offset: int = 0, data: bytes) -> bool:
        self._validate_range(offset, None)
        target = self._resolve_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        mode = "r+b" if target.exists() else "wb+"
        with target.open(mode) as data_file:
            data_file.seek(offset)
            data_file.write(data)
        return True

    def load_page(self, page_id: int) -> Page | None:
        page_path = self._page_path(page_id)
        if not page_path.exists():
            return None
        return Page.deserialize(self.read(str(page_path)))

    def write_page(self, page: Page) -> bool:
        return self.write(str(self._page_path(page.page_id)), data=page.serialize())

    def _page_path(self, page_id: int) -> Path:
        return self._resolve_path(f"{self._PAGE_DIRECTORY}/page_{page_id}.bin")

    def _resolve_path(self, path: str) -> Path:
        candidate = Path(path)
        target = candidate.resolve() if candidate.is_absolute() else (self._root_path / candidate).resolve()
        try:
            target.relative_to(self._root_path)
        except ValueError as error:
            raise StoragePathError(f"Path '{path}' is outside the storage root") from error
        return target

    @staticmethod
    def _validate_range(offset: int, length: int | None) -> None:
        if offset < 0 or (length is not None and length < 0):
            raise ValueError("File offset and length must not be negative")
