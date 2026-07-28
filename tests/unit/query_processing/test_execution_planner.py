from dbms.query_processing.execution_planner import ExecutionPlanner
from dbms.query_processing.sql_parser import SQLParser
from dbms.query_processing.execution_operator import ProjectOperator


def test_execution_planner_can_be_created():
    assert isinstance(ExecutionPlanner(), ExecutionPlanner)


def test_execution_planner_builds_select_iterator_pipeline():
    planner = ExecutionPlanner(
        {"users": [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Grace"}]}
    )
    ast = SQLParser().parse_sql("SELECT name FROM users WHERE id = 2")

    pipeline = planner.build(ast)

    assert isinstance(pipeline, ProjectOperator)
    assert list(pipeline) == [{"name": "Grace"}]
