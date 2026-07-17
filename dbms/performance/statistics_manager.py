class StatisticsManager:
    def __init__(self, statistics: dict | None = None) -> None:
        self.statistics = {} if statistics is None else statistics

    def collect(self) -> bool:
        return True

    def update_histogram(self) -> bool:
        return True

    def estimate_cardinality(self) -> float:
        return 0.0
