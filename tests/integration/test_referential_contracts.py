from dbms.database_object.index_management import IndexManager
from dbms.database_object.metadata_management import Catalog
from dbms.database_object.relationship_management import Relationship, ReferentialActionPolicy
from dbms.database_object.schema_management.schema import ColumnSchema, TableSchema
from dbms.subsystems import DatabaseObjectManager


def test_set_null_updates_every_dependent_row():
    manager = DatabaseObjectManager(Catalog(), IndexManager())
    manager.provision_table("public", "users", TableSchema("users", [ColumnSchema("id", "INT")]))
    manager.provision_table(
        "public",
        "orders",
        TableSchema("orders", [ColumnSchema("user_id", "INT", nullable=True)]),
    )
    manager.relationship_manager.create_relationship(
        Relationship(
            "fk_orders_users",
            "orders",
            "users",
            "MANY_TO_ONE",
            ReferentialActionPolicy(on_delete="SET_NULL"),
            ("user_id",),
            ("id",),
        )
    )
    user_id = manager.insert_row("users", {"id": 7})
    manager.insert_row("orders", {"user_id": 7})
    manager.insert_row("orders", {"user_id": 7})

    manager.delete_row("users", user_id)

    assert [row["user_id"] for row in manager.select_rows("orders")] == [None, None]


def test_unhandled_referential_action_leaves_dependent_rows_unchanged():
    manager = DatabaseObjectManager(Catalog(), IndexManager())
    manager.provision_table("public", "users", TableSchema("users", [ColumnSchema("id", "INT")]))
    manager.provision_table("public", "orders", TableSchema("orders", [ColumnSchema("user_id", "INT")]))
    manager.relationship_manager.create_relationship(
        Relationship(
            "fk_orders_users",
            "orders",
            "users",
            "MANY_TO_ONE",
            ReferentialActionPolicy(on_delete="IGNORE"),
            ("user_id",),
            ("id",),
        )
    )
    user_id = manager.insert_row("users", {"id": 7})
    manager.insert_row("orders", {"user_id": 7})

    manager.delete_row("users", user_id)

    assert manager.select_rows("orders")[0]["user_id"] == 7
