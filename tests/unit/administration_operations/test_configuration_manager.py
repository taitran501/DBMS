from dbms.administration_operations.configuration_manager import ConfigurationManager


def test_configuration_manager_can_be_created():
    assert isinstance(ConfigurationManager(), ConfigurationManager)
