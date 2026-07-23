from dbms.storage_engine.buffer_replacement_strategy import (
    FifoReplacementStrategy,
    LruReplacementStrategy,
)


def test_fifo_selects_the_earliest_eligible_page():
    strategy = FifoReplacementStrategy()
    strategy.record_page(1)
    strategy.record_page(2)

    assert strategy.select_victim([2, 1]) == 1


def test_lru_selects_the_least_recently_accessed_eligible_page():
    strategy = LruReplacementStrategy()
    strategy.record_page(1)
    strategy.record_page(2)
    strategy.record_access(1)

    assert strategy.select_victim([1, 2]) == 2


def test_removed_page_is_not_selected_as_a_victim():
    strategy = FifoReplacementStrategy()
    strategy.record_page(1)
    strategy.record_page(2)
    strategy.remove_page(1)

    assert strategy.select_victim([1, 2]) == 2
