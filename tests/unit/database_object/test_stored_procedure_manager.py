from dbms.database_object.stored_procedure_manager import StoredProcedureManager


def test_stored_procedure_manager_can_be_created():
    assert isinstance(StoredProcedureManager(), StoredProcedureManager)
