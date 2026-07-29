import pytest

from dbms.query_processing.execution_operator import (
    FilterOperator,
    IndexScanOperator,
    ParallelTableScanOperator,
    ProjectOperator,
    SeqScanOperator,
)
from dbms.query_processing.ast import BinaryOpNode, IdentifierNode, LiteralNode
from dbms.query_processing.execution_plan_factory import (
    ExecutionPlanFactory,
    FilterOperatorFactory,
    ProjectOperatorFactory,
    SeqScanOperatorFactory,
    UnknownOperatorError,
)


def test_seq_scan_factory_creates_operator():
    data_sources = {"users": [{"id": 1, "name": "Alice"}]}
    factory = SeqScanOperatorFactory()
    op = factory.create_operator("SequentialScan(users)", data_sources=data_sources)

    assert isinstance(op, SeqScanOperator)
    assert op.table_name == "users"
    assert op.records == [{"id": 1, "name": "Alice"}]


def test_filter_factory_creates_operator():
    child_scan = SeqScanOperator([{"id": 1}], "users")
    factory = FilterOperatorFactory()
    op = factory.create_operator("Filter(id = 1)", child=child_scan)

    assert isinstance(op, FilterOperator)
    assert op.child is child_scan
    assert isinstance(op.predicate, BinaryOpNode)
    assert isinstance(op.predicate.left, IdentifierNode)
    assert op.predicate.left.name == "id"
    assert op.predicate.operator == "="
    assert isinstance(op.predicate.right, LiteralNode)
    assert op.predicate.right.value == 1


def test_filter_factory_without_child_raises_value_error():
    factory = FilterOperatorFactory()
    with pytest.raises(ValueError, match="requires a valid child"):
        factory.create_operator("Filter(id = 1)")


def test_project_factory_creates_operator():
    child_scan = SeqScanOperator([{"id": 1, "name": "Alice"}], "users")
    factory = ProjectOperatorFactory()
    op = factory.create_operator("Project(id, name)", child=child_scan)

    assert isinstance(op, ProjectOperator)
    assert op.child is child_scan
    assert op.columns == ["id", "name"]


def test_project_factory_without_child_raises_value_error():
    factory = ProjectOperatorFactory()
    with pytest.raises(ValueError, match="requires a valid child"):
        factory.create_operator("Project(id)")


def test_execution_plan_factory_build_pipeline():
    data_sources = {"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}
    plan_factory = ExecutionPlanFactory(data_sources=data_sources)

    pipeline = plan_factory.build_pipeline(
        ["SequentialScan(users)", "Filter(id = 1)", "Project(name)"]
    )

    assert isinstance(pipeline, ProjectOperator)
    assert isinstance(pipeline.child, FilterOperator)
    assert isinstance(pipeline.child.child, SeqScanOperator)


def test_execution_plan_factory_pipeline_filters_and_projects_rows():
    data_sources = {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ]
    }
    plan_factory = ExecutionPlanFactory(data_sources=data_sources)

    pipeline = plan_factory.build_pipeline(
        ["SequentialScan(users)", "Filter(id = 1)", "Project(name)"]
    )

    assert list(pipeline) == [{"name": "Alice"}]


def test_filter_factory_parses_boolean_predicate():
    child_scan = SeqScanOperator([{"id": 1}], "users")
    factory = FilterOperatorFactory()

    op = factory.create_operator("Filter(True)", child=child_scan)

    assert isinstance(op.predicate, LiteralNode)
    assert op.predicate.value is True


def test_execution_plan_factory_unknown_operator_raises_error():
    plan_factory = ExecutionPlanFactory()
    with pytest.raises(UnknownOperatorError, match="No factory registered"):
        plan_factory.build_operator("UnknownOp(users)")


def test_execution_plan_factory_builds_index_scan_for_optimizer_descriptor():
    factory = ExecutionPlanFactory(
        {"users": [{"id": 1, "name": "Ada"}, {"id": 2, "name": "Grace"}]}
    )

    pipeline = factory.build_pipeline(["IndexScan(users, users_pk, id = 2)"])

    assert isinstance(pipeline, IndexScanOperator)
    assert pipeline.index_name == "users_pk"
    assert list(pipeline) == [{"id": 2, "name": "Grace"}]


def test_execution_plan_factory_builds_parallel_scan_in_source_order():
    records = [{"id": 1}, {"id": 2}, {"id": 3}]
    factory = ExecutionPlanFactory({"users": records})

    pipeline = factory.build_pipeline(["ParallelTableScan(users)"])

    assert isinstance(pipeline, ParallelTableScanOperator)
    assert list(pipeline) == records
