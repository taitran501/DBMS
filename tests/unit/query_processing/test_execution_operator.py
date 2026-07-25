import pytest

from dbms.query_processing.ast import BinaryOpNode, IdentifierNode, LiteralNode
from dbms.query_processing.execution_operator import (
    ExecutionOperator,
    FilterOperator,
    ProjectOperator,
    SeqScanOperator,
)


@pytest.fixture
def sample_dataset():
    return [
        {"id": 1, "name": "Alice", "age": 25, "city": "Hanoi"},
        {"id": 2, "name": "Bob", "age": 17, "city": "Danang"},
        {"id": 3, "name": "Charlie", "age": 30, "city": "Saigon"},
        {"id": 4, "name": "David", "age": 16, "city": "Hanoi"},
    ]


def test_seq_scan_operator_yields_rows_in_stream(sample_dataset):
    # Arrange
    scan_op = SeqScanOperator(sample_dataset, table_name="users")

    # Act
    scan_op.open()
    r1 = scan_op.next()
    r2 = scan_op.next()
    r3 = scan_op.next()
    r4 = scan_op.next()
    r5 = scan_op.next()
    scan_op.close()

    # Assert
    assert r1 == sample_dataset[0]
    assert r2 == sample_dataset[1]
    assert r3 == sample_dataset[2]
    assert r4 == sample_dataset[3]
    assert r5 is None


def test_filter_operator_filters_rows_via_interpreter_ast(sample_dataset):
    # Arrange: WHERE age >= 18
    scan_op = SeqScanOperator(sample_dataset)
    predicate = BinaryOpNode(IdentifierNode("age"), ">=", LiteralNode(18))
    filter_op = FilterOperator(child=scan_op, predicate=predicate)

    # Act
    filter_op.open()
    adults = []
    while True:
        row = filter_op.next()
        if row is None:
            break
        adults.append(row)
    filter_op.close()

    # Assert
    assert len(adults) == 2
    assert [r["name"] for r in adults] == ["Alice", "Charlie"]


def test_project_operator_projects_selected_columns(sample_dataset):
    # Arrange: SELECT name, city
    scan_op = SeqScanOperator(sample_dataset)
    project_op = ProjectOperator(child=scan_op, columns=["name", "city"])

    # Act
    project_op.open()
    projected_rows = []
    while True:
        row = project_op.next()
        if row is None:
            break
        projected_rows.append(row)
    project_op.close()

    # Assert
    assert len(projected_rows) == 4
    assert projected_rows[0] == {"name": "Alice", "city": "Hanoi"}
    assert projected_rows[1] == {"name": "Bob", "city": "Danang"}


def test_chained_pipeline_executes_scan_filter_project(sample_dataset):
    # Arrange: SELECT name, age FROM users WHERE age >= 18
    scan_op = SeqScanOperator(sample_dataset, table_name="users")
    predicate = BinaryOpNode(IdentifierNode("age"), ">=", LiteralNode(18))
    filter_op = FilterOperator(child=scan_op, predicate=predicate)
    pipeline = ProjectOperator(child=filter_op, columns=["name", "age"])

    # Act
    pipeline.open()
    results = []
    while True:
        row = pipeline.next()
        if row is None:
            break
        results.append(row)
    pipeline.close()

    # Assert
    assert results == [
        {"name": "Alice", "age": 25},
        {"name": "Charlie", "age": 30},
    ]


def test_operator_python_iterator_protocol(sample_dataset):
    # Arrange: SELECT name FROM users WHERE age < 18
    scan_op = SeqScanOperator(sample_dataset)
    predicate = BinaryOpNode(IdentifierNode("age"), "<", LiteralNode(18))
    filter_op = FilterOperator(child=scan_op, predicate=predicate)
    pipeline = ProjectOperator(child=filter_op, columns=["name"])

    # Act: Use standard Python for-loop iteration
    minors = list(pipeline)

    # Assert
    assert minors == [{"name": "Bob"}, {"name": "David"}]


def test_operator_open_resets_stream(sample_dataset):
    # Arrange
    scan_op = SeqScanOperator(sample_dataset)

    # Act
    scan_op.open()
    r1 = scan_op.next()
    scan_op.open()  # reset stream back to position 0
    r2 = scan_op.next()
    scan_op.close()

    # Assert
    assert r1 == r2 == sample_dataset[0]
