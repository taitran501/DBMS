from dbms.query_processing.execution_planner import ExecutionPlanner
from dbms.query_processing.sql_parser import SQLParser
from dbms.query_processing.execution_operator import (
    IndexScanOperator,
    ParallelTableScanOperator,
    ProjectOperator,
)


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


def test_execution_planner_uses_index_scan_when_metadata_selects_one():
    planner = ExecutionPlanner(
        {"users": [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Grace"}]},
        available_indexes={"id": "users_pk"},
    )
    ast = SQLParser().parse_sql("SELECT name FROM users WHERE id = 2")

    pipeline = planner.build(ast)

    assert isinstance(pipeline, ProjectOperator)
    assert isinstance(pipeline.child, IndexScanOperator)
    assert list(pipeline) == [{"name": "Grace"}]


def test_execution_planner_uses_parallel_scan_for_high_cardinality_table():
    records = [{"id": 1}, {"id": 2}, {"id": 3}]
    planner = ExecutionPlanner(
        {"users": records}, table_cardinalities={"users": 10_000}
    )
    ast = SQLParser().parse_sql("SELECT * FROM users")

    pipeline = planner.build(ast)

    assert isinstance(pipeline, ParallelTableScanOperator)
    assert list(pipeline) == records
