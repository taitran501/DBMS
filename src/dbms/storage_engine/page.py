import base64
import json


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

    def serialize(self) -> bytes:
        payload = {
            "page_id": self.page_id,
            "data": base64.b64encode(self.data).decode("ascii"),
            "slots": {
                str(slot_id): base64.b64encode(value).decode("ascii")
                for slot_id, value in self._slots.items()
            },
        }
        return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")

    @classmethod
    def deserialize(cls, payload: bytes) -> "Page":
        data = json.loads(payload.decode("utf-8"))
        page = cls(
            page_id=data["page_id"],
            data=base64.b64decode(data["data"]),
        )
        page._slots = {
            int(slot_id): base64.b64decode(value)
            for slot_id, value in data["slots"].items()
        }
        return page
