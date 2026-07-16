from dbms.query_processing.query_optimizer import QueryOptimizer

def test_estimate_cost():
    pass

def test_select_lowest_cost_plan():
    pass

def test_reorder_join():
    pass

def test_select_index():
    pass

def test_push_predicate():
    pass

def test_use_safe_estimate_without_statistics():
    pass

def test_preserve_query_result():
    pass

def test_query_optimizer_can_be_created():
    assert isinstance(QueryOptimizer(), QueryOptimizer)
