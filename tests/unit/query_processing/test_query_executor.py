from unittest.mock import Mock

import pytest

from dbms.query_processing.query_executor import QueryExecutor
from dbms.query_processing.physical_plan import PhysicalPlan


def test_execute_query_plan():
    # Arrange
    plan = PhysicalPlan(["SequentialScan(users)"])
    plan.rows = [{"id": 1}, {"id": 2}]

    # Act
    result = QueryExecutor().execute(plan)

    # Assert
    assert result == [{"id": 1}, {"id": 2}]


def test_fetch():
    # Arrange
    executor = QueryExecutor()
    executor.results = [{"id": 1}, {"id": 2}]

    # Act
    result = executor.fetch()

    # Assert
    # fetch() returns rows buffered by the latest execution.
    assert result == [{"id": 1}, {"id": 2}]

def test_execute_select():
    # Arrange
    plan = PhysicalPlan(["SequentialScan(users)"])
    plan.rows = [{"id": 1}]

    # Act
    result = QueryExecutor().execute_select(plan)

    # Assert
    assert result == [{"id": 1}]

def test_execute_insert():
    # Arrange
    plan = PhysicalPlan(["Insert(users)"])
    plan.rows = [{"id": 1}]

    # Act
    result = QueryExecutor().execute_insert(plan)

    # Assert
    # Write operations report affected rows, not the inserted values.
    assert result == 1

def test_execute_update():
    # Arrange
    plan = PhysicalPlan(["Update(users)"])
    plan.matched_rows = 2

    # Act
    result = QueryExecutor().execute_update(plan)

    # Assert
    assert result == 2

def test_execute_delete():
    # Arrange
    plan = PhysicalPlan(["Delete(users)"])
    plan.matched_rows = 2

    # Act
    result = QueryExecutor().execute_delete(plan)

    # Assert
    assert result == 2

def test_execute_filter():
    # Arrange
    plan = PhysicalPlan(["Filter(age >= 18)"])
    plan.rows = [{"age": 17}, {"age": 18}, {"age": 25}]

    # Act
    result = QueryExecutor().execute_filter(plan)

    # Assert
    assert result == [{"age": 18}, {"age": 25}]

def test_execute_join():
    # Arrange
    plan = PhysicalPlan(["Join(users.id = orders.user_id)"])
    plan.left_rows = [{"id": 1}, {"id": 2}]
    plan.right_rows = [{"user_id": 2, "total": 50}]

    # Act
    result = QueryExecutor().execute_join(plan)

    # Assert
    # Only rows satisfying the join key are combined.
    assert result == [{"id": 2, "user_id": 2, "total": 50}]

def test_execute_aggregation():
    # Arrange
    plan = PhysicalPlan(["Sum(amount)"])
    plan.rows = [10, 20, 30]

    # Act
    result = QueryExecutor().execute_aggregation(plan)

    # Assert
    assert result == 60

def test_return_empty_result():
    # Arrange
    plan = PhysicalPlan(["SequentialScan(empty_table)"])
    plan.rows = []

    # Act
    result = QueryExecutor().execute_select(plan)

    # Assert
    assert result == []

def test_rollback_on_failure():
    # Arrange
    transaction = Mock()
    plan = PhysicalPlan(["Insert(users)"])
    plan.error = RuntimeError("write failed")

    # Act
    with pytest.raises(RuntimeError, match="write failed"):
        QueryExecutor().execute(plan, transaction)

    # Assert
    # A failed write must not leave a partially applied transaction.
    transaction.rollback.assert_called_once_with()

def test_query_executor_can_be_created():
    # Arrange
    executor_type = QueryExecutor

    # Act
    executor = executor_type()

    # Assert
    assert isinstance(executor, QueryExecutor)


def test_execute_group_by():
    # Arrange
    plan = PhysicalPlan(["GroupBy(department)", "Count(*)"])
    plan.rows = ["engineering", "engineering", "sales"]

    # Act
    result = QueryExecutor().execute_aggregation(plan)

    # Assert
    # Equal group keys are combined before the aggregate is calculated.
    assert result == {"engineering": 2, "sales": 1}

def test_execute_sort():
    # Arrange
    plan = PhysicalPlan(["Sort(age ASC)"])
    plan.rows = [30, 20, 25]

    # Act
    result = QueryExecutor().execute_sort(plan)

    # Assert
    assert result == [20, 25, 30]

def test_execute_parallel():
    # Arrange
    plan = PhysicalPlan(["ParallelTableScan(users)"])
    plan.partitions = [[1, 3], [2, 4]]

    # Act
    result = QueryExecutor().execute_parallel(plan)

    # Assert
    # Every worker partition contributes once to the merged result.
    assert sorted(result) == [1, 2, 3, 4]

def test_cancel_execution():
    # Arrange
    executor = QueryExecutor()

    # Act
    result = executor.cancel_execution()

    # Assert
    # True confirms that the cancellation request was accepted.
    assert result is True
