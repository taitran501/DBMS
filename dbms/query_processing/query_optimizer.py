from dbms.query_processing.logical_plan import LogicalPlan
from dbms.query_processing.physical_plan import PhysicalPlan


class QueryOptimizer:
    def __init__(self) -> None:
        self.rules: list = []

    def optimize(self, plan: LogicalPlan) -> PhysicalPlan | None:
        return None

    def estimate_cost(self, plan: LogicalPlan) -> float | None:
        return None
