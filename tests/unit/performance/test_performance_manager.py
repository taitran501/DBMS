from dbms.performance.performance_manager import PerformanceManager


def test_performance_manager_can_be_created():
    assert isinstance(PerformanceManager(), PerformanceManager)
