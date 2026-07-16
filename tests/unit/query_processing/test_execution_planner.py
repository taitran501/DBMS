from dbms.query_processing.execution_planner import ExecutionPlanner


def test_execution_planner_can_be_created():
    assert isinstance(ExecutionPlanner(), ExecutionPlanner)
