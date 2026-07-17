from dbms.database_object.stored_procedure import StoredProcedure


def test_stored_procedure_can_be_created():
    query_plan = object()
    query_executor = object()
    procedure = StoredProcedure("p1", "calculate_total", query_plan, query_executor)

    assert procedure.procedure_id == "p1"
    assert procedure.name == "calculate_total"
    assert procedure.query_plan is query_plan
    assert procedure.query_executor is query_executor
    assert callable(procedure.execute)


def test_execute_stored_procedure():
    pass
