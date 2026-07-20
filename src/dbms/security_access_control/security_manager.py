class SecurityManager:
    def __init__(self, users: list | None = None, roles: list | None = None) -> None:
        self.users = [] if users is None else users
        self.roles = [] if roles is None else roles

    def authenticate(self) -> bool:
        return True

    def authorize(self) -> bool:
        return True
