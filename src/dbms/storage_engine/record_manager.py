from dbms.database_object.row import Row
from dbms.storage_engine.exceptions import RecordNotFoundError
from dbms.storage_engine.page_manager import PageManager
from dbms.storage_engine.record_mapper import RecordMapper


class RecordManager:
    """Stores Rows in Pages by using a RecordMapper at the storage boundary."""

    def __init__(
        self,
        page_manager: PageManager,
        mapper: RecordMapper | None = None,
    ) -> None:
        self.page_manager = page_manager
        self.mapper = mapper or RecordMapper()

    def insert_row(self, row: Row) -> str:
        payload = self.mapper.serialize(row)
        page = self.page_manager.get_page_with_free_space(len(payload))
        try:
            slot_id = page.insert_tuple(payload)
            return self._location(page.page_id, slot_id)
        finally:
            self.page_manager.release_page(page.page_id)

    def read_row(self, location: str) -> Row:
        page_id, slot_id = self._parse_location(location)
        page = self._get_page(page_id, location)
        try:
            payload = page.read_tuple(slot_id)
            if payload is None:
                raise RecordNotFoundError(f"Record '{location}' was not found")
            return self.mapper.deserialize(payload)
        finally:
            self.page_manager.release_page(page_id)

    def update_row(self, location: str, row: Row) -> bool:
        page_id, slot_id = self._parse_location(location)
        page = self._get_page(page_id, location)
        try:
            if page.read_tuple(slot_id) is None:
                raise RecordNotFoundError(f"Record '{location}' was not found")
            return page.write_tuple(slot_id, self.mapper.serialize(row))
        finally:
            self.page_manager.release_page(page_id)

    def delete_row(self, location: str) -> bool:
        page_id, slot_id = self._parse_location(location)
        page = self._get_page(page_id, location)
        try:
            if not page.delete_tuple(slot_id):
                raise RecordNotFoundError(f"Record '{location}' was not found")
            return True
        finally:
            self.page_manager.release_page(page_id)

    @staticmethod
    def _location(page_id: int, slot_id: int) -> str:
        return f"{page_id}:{slot_id}"

    @staticmethod
    def _parse_location(location: str) -> tuple[int, int]:
        try:
            page_id, slot_id = (int(value) for value in location.split(":", maxsplit=1))
        except (TypeError, ValueError) as error:
            raise RecordNotFoundError(f"Invalid record location '{location}'") from error
        return page_id, slot_id

    def _get_page(self, page_id: int, location: str):
        page = self.page_manager.get_page(page_id)
        if page is None:
            raise RecordNotFoundError(f"Record '{location}' was not found")
        return page
