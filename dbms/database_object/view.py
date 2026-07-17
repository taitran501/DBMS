class View:
    def __init__(self, view_id: str = "", name: str = "", query_definition: str = "") -> None:
        self.view_id = view_id
        self.name = name
        self.query_definition = query_definition

    def create_view(self) -> bool:
        return True

    def refresh(self) -> bool:
        return True
