class PhysicalPlan:
    def __init__(self, operators: list) -> None:
        self.operators = operators

    def generate(self) -> bool:
        return True
