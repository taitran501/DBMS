from dbms.query_processing.query_validator import QueryValidator

def test_validate_table():
    pass

def test_validate_column():
    pass

def test_validate_data_type():
    pass

def test_validate_permission():
    pass

def test_reject_unknown_table():
    pass

def test_reject_unknown_column():
    pass

def test_reject_type_mismatch():
    pass

def test_reject_unauthorized_query():
    pass

def test_query_validator_can_be_created():
    assert isinstance(QueryValidator(), QueryValidator)
