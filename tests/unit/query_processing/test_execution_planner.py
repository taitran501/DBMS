from dbms.query_processing.execution_planner import ExecutionPlanner

def test_create_logical_plan():
    pass

def test_create_physical_plan():
    pass

def test_plan_table_scan():
    pass

def test_plan_index_scan():
    pass

def test_plan_join():
    pass

def test_plan_aggregation():
    pass

def test_reject_invalid_plan():
    pass

def test_execution_planner_can_be_created():
    assert isinstance(ExecutionPlanner(), ExecutionPlanner)
