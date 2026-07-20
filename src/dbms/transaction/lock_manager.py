class LockManager:
    def acquire_lock(self, transaction: object, resource: str, mode: str) -> bool:
        return False

    def release_lock(self, transaction: object, resource: str) -> bool:
        return False
