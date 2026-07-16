from dbms.durability.checkpoint_manager import CheckpointManager


def test_checkpoint_manager_can_be_created():
    assert isinstance(CheckpointManager(), CheckpointManager)
