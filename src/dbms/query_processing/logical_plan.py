class LogicalPlan:
    def __init__(self, operators: list) -> None:
        self.operators = operators

    def build(self) -> bool:
        return True
