from dbms.query_processing.query_optimizer import QueryOptimizer
from dbms.query_processing.logical_plan import LogicalPlan
from dbms.query_processing.physical_plan import PhysicalPlan


def test_optimize():
    # Arrange
    plan = LogicalPlan(["TableScan(users)"])

    # Act
    result = QueryOptimizer().optimize(plan)

    # Assert
    assert isinstance(result, PhysicalPlan)

def test_estimate_cost():
    # Arrange
    plan = LogicalPlan(["TableScan(users)", "Filter(active = true)"])
    plan.operator_costs = [10.0, 5.5]

    # Act
    result = QueryOptimizer().estimate_cost(plan)

    # Assert
    # Total plan cost includes every operator in the execution path.
    assert result == 15.5

def test_select_lowest_cost_plan():
    # Arrange
    low_cost_plan = LogicalPlan(["IndexScan(users)"])
    low_cost_plan.estimated_cost = 5.0
    high_cost_plan = LogicalPlan(["TableScan(users)"])
    high_cost_plan.estimated_cost = 20.0

    # Act
    result = QueryOptimizer().select_lowest_cost_plan(
        [high_cost_plan, low_cost_plan]
    )

    # Cost-based optimization chooses the cheapest equivalent plan.
    assert result is low_cost_plan

def test_reorder_join():
    # Arrange
    plan = LogicalPlan(["Join(large_table, small_table)"])
    plan.table_cardinalities = {"large_table": 10_000, "small_table": 10}

    # Act
    result = QueryOptimizer().optimize(plan)

    # Assert
    assert result.operators == ["Join(small_table, large_table)"]

def test_select_index():
    # Arrange
    plan = LogicalPlan(["TableScan(users)", "Filter(id = 10)"])
    plan.available_indexes = {"id": "users_pk"}

    # Act
    result = QueryOptimizer().optimize(plan)

    # Assert
    # An indexed equality predicate replaces a full table scan.
    assert result.operators == ["IndexScan(users, users_pk, id = 10)"]

def test_push_predicate():
    # Arrange
    plan = LogicalPlan(["Join(users, orders)", "Filter(users.active = true)"])

    # Act
    result = QueryOptimizer().optimize(plan)

    # Assert
    # Filtering users before the join reduces the rows entering the join.
    assert result.operators == [
        "Filter(users.active = true)",
        "Join(users, orders)",
    ]

def test_use_safe_estimate_without_statistics():
    # Arrange
    plan = LogicalPlan(["TableScan(users)"])

    # Act
    result = QueryOptimizer().estimate_cost(plan)

    # Assert
    assert isinstance(result, float)
    assert result > 0

def test_preserve_query_result():
    # Arrange
    plan = LogicalPlan(["TableScan(users)", "Project(id, name)"])
    plan.output_columns = ["id", "name"]

    # Act
    result = QueryOptimizer().optimize(plan)

    # Assert
    # Optimization may change operators, but not the query's output contract.
    assert result.output_columns == ["id", "name"]

def test_query_optimizer_can_be_created():
    # Arrange
    optimizer_type = QueryOptimizer

    # Act
    optimizer = optimizer_type()

    # Assert
    assert isinstance(optimizer, QueryOptimizer)


def test_constant_folding():
    # Arrange
    plan = LogicalPlan(["Filter(1 + 1 = 2)"])

    # Act
    result = QueryOptimizer().optimize(plan)

    # Assert
    # A constant expression is evaluated once during optimization.
    assert result.operators == ["Filter(True)"]

def test_projection_pruning():
    # Arrange
    plan = LogicalPlan(["TableScan(users: id, name, email)", "Project(id)"])

    # Act
    result = QueryOptimizer().optimize(plan)

    # Assert
    # Unused columns are removed from the scan as early as possible.
    assert result.operators == ["TableScan(users: id)", "Project(id)"]

def test_estimate_cardinality():
    # Arrange
    plan = LogicalPlan(["Filter(active = true)"])
    plan.row_count = 1_000
    plan.selectivity = 0.1

    # Act
    result = QueryOptimizer().estimate_cardinality(plan)

    # Assert
    # Estimated output rows are input rows multiplied by predicate selectivity.
    assert result == 100

def test_choose_parallel_plan():
    # Arrange
    plan = LogicalPlan(["TableScan(large_table)"])
    plan.estimated_cost = 10_000

    # Act
    result = QueryOptimizer().optimize(plan)

    # Assert
    # Expensive scans can be divided between parallel workers.
    assert "ParallelTableScan(large_table)" in result.operators

def test_generate_physical_plan():
    # Arrange
    plan = LogicalPlan(["TableScan(users)"])

    # Act
    result = QueryOptimizer().generate_physical_plan(plan)

    # Assert
    assert isinstance(result, PhysicalPlan)
    assert result.operators == ["SequentialScan(users)"]
    # Assert
