from dbms.administration_operations.monitoring_manager import MonitoringManager


def test_monitoring_manager_can_be_created():
    assert isinstance(MonitoringManager(), MonitoringManager)
