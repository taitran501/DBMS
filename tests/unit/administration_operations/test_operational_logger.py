from dbms.administration_operations.operational_logger import OperationalLogger


def test_operational_logger_can_be_created():
    assert isinstance(OperationalLogger(), OperationalLogger)
