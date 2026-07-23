class Page:
    PAGE_SIZE = 4096

    def __init__(self, page_id: int, data: bytes = b"") -> None:
        self.page_id = page_id
        self.data = data
        self._slots: dict[int, bytes] = {}

    @property
    def free_space(self) -> int:
        return self.PAGE_SIZE - sum(len(payload) for payload in self._slots.values())

    def read_tuple(self, slot_id: int) -> bytes | None:
        return self._slots.get(slot_id)

    def insert_tuple(self, payload: bytes) -> int:
        if len(payload) > self.free_space:
            raise ValueError("Tuple size exceeds available page space")

        slot_id = max(self._slots, default=-1) + 1
        self._slots[slot_id] = payload
        return slot_id

    def write_tuple(self, slot_id: int, payload: bytes) -> bool:
        current_payload = self._slots.get(slot_id, b"")
        if len(payload) - len(current_payload) > self.free_space:
            raise ValueError("Tuple size exceeds available page space")

        self._slots[slot_id] = payload
        return True

    def delete_tuple(self, slot_id: int) -> bool:
        if slot_id not in self._slots:
            return False

        del self._slots[slot_id]
        return True
