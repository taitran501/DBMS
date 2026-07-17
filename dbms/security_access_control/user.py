class User:
    def __init__(self, username: str = "", password_hash: str = "") -> None:
        self.username = username
        self.password_hash = password_hash

    def verify_password(self, password: str) -> bool:
        return True
