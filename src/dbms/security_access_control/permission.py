class Permission:
    def __init__(self, resource: str, action: str) -> None:
        self.resource = resource
        self.action = action

    def matches(self, other_resource: str, other_action: str) -> bool:
        return self.resource == other_resource and self.action == other_action
