class Role:
    def __init__(self, role_name: str = "", permissions: list | None = None) -> None:
        self.role_name = role_name
        self.permissions = [] if permissions is None else permissions

    def grant(self, permission: object) -> bool:
        return True

    def revoke(self, permission: object) -> bool:
        return True
