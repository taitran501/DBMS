from dbms.dbms import DBMS


def test_dbms_can_be_created():
    assert isinstance(DBMS(), DBMS)
