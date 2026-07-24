from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock

import pytest

from dbms.storage_engine.buffer_pool import BufferPool
from dbms.storage_engine.dependencies import PageStoreProtocol


def test_get_instance_returns_same_instance():
    # Arrange & Act
    pool1 = BufferPool.get_instance(capacity=5)
    pool2 = BufferPool.get_instance(capacity=5)

    # Assert
    assert pool1 is pool2
    assert isinstance(pool1, BufferPool)
    assert pool1.capacity == 5


def test_get_instance_initializes_with_parameters():
    # Arrange
    mock_store = Mock(spec=PageStoreProtocol)

    # Act
    pool = BufferPool.get_instance(capacity=20, page_store=mock_store)

    # Assert
    assert pool.capacity == 20
    assert pool.page_store is mock_store


def test_reset_instance_clears_singleton():
    # Arrange
    pool1 = BufferPool.get_instance(capacity=10)

    # Act
    BufferPool.reset_instance()
    pool2 = BufferPool.get_instance(capacity=15)

    # Assert
    assert pool1 is not pool2
    assert pool2.capacity == 15


def test_reject_get_instance_with_different_configuration():
    # Arrange
    pool1 = BufferPool.get_instance(capacity=8)

    # Act / Assert
    with pytest.raises(ValueError, match="configured differently"):
        BufferPool.get_instance(capacity=50)


def test_reject_get_instance_with_different_page_store():
    first_store = Mock(spec=PageStoreProtocol)
    BufferPool.get_instance(capacity=8, page_store=first_store)

    with pytest.raises(ValueError, match="configured differently"):
        BufferPool.get_instance(page_store=Mock(spec=PageStoreProtocol))


def test_direct_construction_returns_the_singleton_instance():
    pool1 = BufferPool.get_instance(capacity=8)

    pool2 = BufferPool(capacity=8)

    assert pool1 is pool2


def test_direct_construction_rejects_different_configuration():
    BufferPool.get_instance(capacity=8)

    with pytest.raises(ValueError, match="configured differently"):
        BufferPool(capacity=50)


def test_concurrent_get_instance_returns_one_instance():
    with ThreadPoolExecutor(max_workers=8) as executor:
        instances = list(executor.map(lambda _: BufferPool.get_instance(), range(16)))

    assert len({id(pool) for pool in instances}) == 1


def test_concurrent_direct_construction_returns_one_instance():
    with ThreadPoolExecutor(max_workers=8) as executor:
        instances = list(executor.map(lambda _: BufferPool(capacity=10), range(16)))

    assert len({id(pool) for pool in instances}) == 1
