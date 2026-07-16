from dbms.durability.cluster_node import ClusterNode


def test_cluster_node_can_be_created():
    node = ClusterNode("node1", "127.0.0.1:8080")
    assert node.node_id == "node1"
    assert node.address == "127.0.0.1:8080"


def test_ping():
    node = ClusterNode("node1", "127.0.0.1:8080")
    assert node.ping() is True
