class StoredProcedure:
    def __init__(self, procedure_id: str = "", name: str = "") -> None:
        self.procedure_id = procedure_id
        self.name = name

    def execute(self) -> object:
        return None
