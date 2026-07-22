import pytest

from dbms.database_object.index import BTreeIndex, HashIndex
from dbms.database_object.index_factory import BTreeIndexFactory, HashIndexFactory


@pytest.mark.parametrize(
    ("factory", "expected_type", "expected_class"),
    [
        (BTreeIndexFactory(), "BTree", BTreeIndex),
        (HashIndexFactory(), "Hash", HashIndex),
    ],
)
def test_create_index_returns_the_product_selected_by_its_factory(
    factory, expected_type, expected_class
):
    # Act
    index = factory.create_index(
        "idx_users_email",
        "users_email",
        columns=["email"],
        unique=True,
    )

    # Assert
    assert isinstance(index, expected_class)
    assert index.index_id == "idx_users_email"
    assert index.name == "users_email"
    assert index.type == expected_type
    assert index.columns == ("email",)
    assert index.unique is True


def test_created_index_does_not_share_the_callers_column_collection():
    # Arrange
    columns = ["email"]

    # Act
    index = BTreeIndexFactory().create_index(
        "idx_users_email", "users_email", columns=columns
    )
    columns.append("tenant_id")

    # Assert
    assert index.columns == ("email",)
