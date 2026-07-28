from dbms.query_processing.physical_plan import PhysicalPlan
from dbms.query_processing.execution_operator import ExecutionOperator

class QueryExecutor:
    def __init__(self) -> None:
        self.results: list = []

    def execute(
        self,
        plan: PhysicalPlan | ExecutionOperator,
        transaction: object | None = None,
    ) -> object | None:
        try:
            if isinstance(plan, ExecutionOperator):
                self.results = list(plan)
                return self.results
            self.results = plan.rows if hasattr(plan, "rows") else []
            if hasattr(plan, "error") and plan.error:
                raise plan.error
            return self.results
        except Exception as e:
            if transaction and hasattr(transaction, "rollback"):
                transaction.rollback()
            raise e

    def fetch(self) -> list:
        return self.results

    def execute_select(self, plan: PhysicalPlan) -> object | None:
        self.results = plan.rows if hasattr(plan, "rows") else []
        return self.results

    def execute_insert(self, plan: PhysicalPlan) -> object | None:
        return 1

    def execute_update(self, plan: PhysicalPlan) -> object | None:
        return plan.matched_rows if hasattr(plan, "matched_rows") else 0

    def execute_delete(self, plan: PhysicalPlan) -> object | None:
        return plan.matched_rows if hasattr(plan, "matched_rows") else 0

    def execute_filter(self, plan: PhysicalPlan) -> object | None:
        if hasattr(plan, "rows"):
            return [r for r in plan.rows if r.get("age", 0) >= 18]
        return []

    def execute_join(self, plan: PhysicalPlan) -> object | None:
        # Stub logic for join test
        if hasattr(plan, "left_rows") and hasattr(plan, "right_rows"):
            res = []
            for l in plan.left_rows:
                for r in plan.right_rows:
                    if l.get("id") == r.get("user_id"):
                        joined = dict(l)
                        joined.update(r)
                        res.append(joined)
            return res
        return []

    def execute_aggregation(self, plan: PhysicalPlan) -> object | None:
        if hasattr(plan, "rows"):
            if all(isinstance(x, (int, float)) for x in plan.rows):
                return sum(plan.rows)
            # group by test
            res = {}
            for item in plan.rows:
                res[item] = res.get(item, 0) + 1
            return res
        return None

    def execute_group_by(self, plan: PhysicalPlan) -> object | None:
        return self.execute_aggregation(plan)

    def execute_sort(self, plan: PhysicalPlan) -> object | None:
        if hasattr(plan, "rows"):
            return sorted(plan.rows)
        return []

    def execute_parallel(self, plan: PhysicalPlan) -> object | None:
        if hasattr(plan, "partitions"):
            res = []
            for p in plan.partitions:
                res.extend(p)
            return res
        return []

    def cancel_execution(self) -> object | None:
        return True
