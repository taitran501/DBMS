from dbms.database_object.stored_procedure import StoredProcedure
from unittest.mock import Mock


def test_stored_procedure_can_be_created():
    query_plan = object()
    query_executor = object()
    procedure = StoredProcedure("p1", "calculate_total", query_plan, query_executor)

    assert procedure.procedure_id == "p1"
    assert procedure.name == "calculate_total"
    assert procedure.query_plan is query_plan
    assert procedure.query_executor is query_executor
    assert callable(procedure.execute)


def test_execute():
    query_plan = object()
    query_executor = Mock()
    query_executor.execute.return_value = [{"total": 100}]
    procedure = StoredProcedure("p1", "calculate_total", query_plan, query_executor)

    result = procedure.execute()

    assert result == [{"total": 100}]
    query_executor.execute.assert_called_once_with(query_plan)
