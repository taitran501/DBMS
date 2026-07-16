from dbms.query_processing.logical_plan import LogicalPlan


def test_logical_plan_can_be_created():
    lp = LogicalPlan(["scan", "filter"])
    assert lp.operators == ["scan", "filter"]


def test_build():
    lp = LogicalPlan(["scan", "filter"])
    assert lp.build() is True
