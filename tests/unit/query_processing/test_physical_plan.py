from dbms.query_processing.physical_plan import PhysicalPlan


def test_physical_plan_can_be_created():
    pp = PhysicalPlan(["seq_scan", "filter_op"])
    assert pp.operators == ["seq_scan", "filter_op"]


def test_generate():
    pp = PhysicalPlan(["seq_scan", "filter_op"])
    assert pp.generate() is True
