import pytest

from dbms.database_object.constraint_management import Constraint
from dbms.database_object.database_management import DatabaseConfiguration
from dbms.database_object.index_management import Index, IndexAccessMethod, IndexManager
from dbms.database_object.metadata_management import Catalog
from dbms.database_object.relationship_management import ReferentialActionPolicy, Relationship
from dbms.database_object.schema_management.schema import ColumnSchema, TableSchema
from dbms.errors import DependencyExistsError
from dbms.subsystems import DatabaseObjectManager


def manager():
    return DatabaseObjectManager(Catalog(), IndexManager())


def test_coordinator_creates_default_schema_and_keeps_same_table_name_isolated_per_database():
    db = manager()
    db.create_database("shop", DatabaseConfiguration(default_schema="public"))
    db.create_database("archive", DatabaseConfiguration(default_schema="public"))
    schema = TableSchema("users", [ColumnSchema("id", "INT", False)])

    db.create_table_in_schema("shop", "public", schema)
    db.create_table_in_schema("archive", "public", schema)
    db.insert_row("shop.public.users", {"id": 1})

    assert db.schema_manager.get_schema("shop", "public").name == "public"
    assert db.select_rows("archive.public.users") == ()
    assert db.metadata_manager.get_metadata("table", "shop.public.users").name == "users"


def test_drop_table_restricts_dependents_and_cascade_removes_all_table_objects():
    db = manager()
    db.create_database("shop")
    db.create_table_in_schema("shop", "public", TableSchema("users", [ColumnSchema("id", "INT", False)]))
    db.create_index_for_table("shop", "public", "users", Index("users_id", IndexAccessMethod.HASH, ["id"], unique=True))
    db.create_constraint_for_table("shop", "public", "users", Constraint("users_id_not_null", "NOT_NULL", ["id"]))
    db.provision_view("shop.public", "active_users", "SELECT * FROM users", ["table:shop.public.users"])
    db.provision_view("other", "unrelated_view", "SELECT 1")
    db.provision_procedure("shop.public", "archive_users", [], "DELETE FROM users", ["table:shop.public.users"])

    with pytest.raises(DependencyExistsError):
        db.drop_table_from_schema("shop", "public", "users")
    db.drop_table_from_schema("shop", "public", "users", cascade=True)

    with pytest.raises(ValueError, match="not found"):
        db.table_manager.find_table("shop.public.users")
    assert "shop.public.users" not in db.index_manager.indexes
    assert "shop.public.users" not in db.constraint_manager.constraints
    assert db.metadata_manager.list_metadata("table", "shop.public") == ()
    with pytest.raises(ValueError, match="not found"):
        db.view_manager.get_view("shop.public", "active_users")
    with pytest.raises(ValueError, match="not found"):
        db.stored_procedure_manager.get_procedure("shop.public", "archive_users")


def test_update_parent_row_applies_cascade_and_set_null_relationship_policies():
    db = manager()
    db.create_database("shop")
    db.create_table_in_schema("shop", "public", TableSchema("parents", [ColumnSchema("id", "INT", False)]))
    db.create_table_in_schema("shop", "public", TableSchema("children", [ColumnSchema("parent_id", "INT")]))
    db.insert_row("shop.public.parents", {"id": 1})
    cascade = Relationship("child_parent", "shop.public.children", "shop.public.parents", "FOREIGN_KEY", ReferentialActionPolicy(on_update="CASCADE"), ["parent_id"], ["id"])
    db.create_relationship(cascade)
    db.insert_row("shop.public.children", {"parent_id": 1})

    db.update_row("shop.public.parents", 1, {"id": 2})
    assert db.select_rows("shop.public.children")[0]["parent_id"] == 2

    nullable = Relationship("child_parent_nullable", "shop.public.children", "shop.public.parents", "FOREIGN_KEY", ReferentialActionPolicy(on_update="SET_NULL"), ["parent_id"], ["id"])
    db.drop_relationship("child_parent")
    db.create_relationship(nullable)
    db.update_row("shop.public.parents", 1, {"id": 3})
    assert db.select_rows("shop.public.children")[0]["parent_id"] is None


def test_rename_database_table_and_column_migrates_canonical_object_references():
    db = manager()
    db.create_database("shop")
    db.create_table_in_schema("shop", "public", TableSchema("users", [ColumnSchema("id", "INT", False), ColumnSchema("email", "TEXT")]))
    db.create_index_for_table("shop", "public", "users", Index("users_email", IndexAccessMethod.HASH, ["email"]))
    db.create_constraint_for_table("shop", "public", "users", Constraint("users_email", "UNIQUE", ["email"]))
    db.provision_trigger("shop.public.users", "audit", "INSERT", "AFTER", lambda context: context)
    db.provision_view("shop.public", "members_view", "SELECT * FROM users", ["table:shop.public.users", "table:unrelated"])
    db.insert_row("shop.public.users", {"id": 1, "email": "a@example.test"})
    db.create_relationship(Relationship("self_ref", "shop.public.users", "shop.public.users", "FOREIGN_KEY", ReferentialActionPolicy(), ["id"], ["id"]))
    db.table_manager.tables["unrelated.public"] = {}

    db.rename_column_in_table("shop", "public", "users", "email", "address")
    db.rename_table_in_schema("shop", "public", "users", "members")
    db.rename_database("shop", "store")

    assert db.select_rows("store.public.members")[0]["address"] == "a@example.test"
    assert db.index_manager.get_index("store.public.members", "users_email").columns == ["address"]
    assert db.constraint_manager.get_constraint("store.public.members", "users_email").columns == ["address"]
    assert db.metadata_manager.get_metadata("table", "store.public.members").name == "members"
    assert "store.public.members" in db.trigger_manager.triggers
    assert db.view_manager._dependency_graph.dependencies["store.public.members_view"] == ["table:store.public.members", "table:unrelated"]


def test_rename_table_without_optional_objects_keeps_empty_manager_scopes_valid():
    db = manager()
    db.create_database("shop")
    db.create_table_in_schema("shop", "public", TableSchema("users", [ColumnSchema("id", "INT")]))
    db.metadata_manager.statistics_manager.stats.pop("shop.public.users")

    db.rename_table_in_schema("shop", "public", "users", "members")

    assert db.table_manager.find_table("shop.public.members").name == "members"


def test_drop_database_cascade_removes_its_schemas_tables_and_metadata():
    db = manager()
    db.create_database("shop")
    db.create_table_in_schema("shop", "public", TableSchema("users", [ColumnSchema("id", "INT")]))
    db.table_manager.tables["unrelated.public"] = {}
    db.metadata_manager.remove_metadata("schema", "shop.public", cascade=True)

    db.drop_database("shop", cascade=True)

    with pytest.raises(ValueError, match="not found"):
        db.database_manager.get_database("shop")
    assert db.schema_manager.schemas.get("shop") is None
    assert db.metadata_manager.list_metadata("table", "shop") == ()


def test_update_parent_row_rejects_no_action_and_unknown_policy_but_allows_unchanged_key():
    db = manager()
    db.create_database("shop")
    db.create_table_in_schema("shop", "public", TableSchema("parents", [ColumnSchema("id", "INT", False)]))
    db.create_table_in_schema("shop", "public", TableSchema("children", [ColumnSchema("parent_id", "INT")]))
    db.insert_row("shop.public.parents", {"id": 1})
    db.insert_row("shop.public.children", {"parent_id": 1})
    db.create_relationship(Relationship("no_action", "shop.public.children", "shop.public.parents", "FOREIGN_KEY", ReferentialActionPolicy(on_update="NO_ACTION"), ["parent_id"], ["id"]))

    db.update_row("shop.public.parents", 1, {"id": 1})
    with pytest.raises(ValueError, match="prevents update"):
        db.update_row("shop.public.parents", 1, {"id": 2})
    db.drop_relationship("no_action")
    db.create_relationship(Relationship("unknown", "shop.public.children", "shop.public.parents", "FOREIGN_KEY", ReferentialActionPolicy(on_update="MERGE"), ["parent_id"], ["id"]))
    with pytest.raises(ValueError, match="unsupported"):
        db.update_row("shop.public.parents", 1, {"id": 2})


def test_canonical_dml_uses_the_same_index_and_relationship_namespace_as_ddl():
    db = manager()
    db.create_database("shop")
    db.create_table_in_schema("shop", "public", TableSchema("parents", [ColumnSchema("id", "INT", False)]))
    db.create_table_in_schema("shop", "public", TableSchema("children", [ColumnSchema("parent_id", "INT")]))
    db.create_index_for_table("shop", "public", "parents", Index("parents_id", IndexAccessMethod.HASH, ["id"], unique=True))
    db.create_relationship(Relationship("child_parent", "shop.public.children", "shop.public.parents", "FOREIGN_KEY", ReferentialActionPolicy(), ["parent_id"], ["id"]))

    db.insert_row("shop.public.parents", {"id": 1})
    with pytest.raises(ValueError, match="Unique index"):
        db.insert_row("shop.public.parents", {"id": 1})
    with pytest.raises(ValueError, match="Relationship child_parent rejected row"):
        db.insert_row("shop.public.children", {"parent_id": 2})


def test_scoped_views_and_procedures_follow_database_rename_and_cascade_without_cross_scope_cleanup():
    db = manager()
    for database_name in ("shop", "archive"):
        db.create_database(database_name)
        db.create_table_in_schema(database_name, "public", TableSchema("users", [ColumnSchema("id", "INT")]))
        db.provision_view(f"{database_name}.public", "active_users", "SELECT * FROM users", [f"table:{database_name}.public.users"])
        db.provision_procedure(f"{database_name}.public", "archive_users", [], "DELETE FROM users", [f"table:{database_name}.public.users"])

    db.rename_database("shop", "store")

    assert db.view_manager.get_view("store.public", "active_users").name == "active_users"
    assert db.stored_procedure_manager.get_procedure("store.public", "archive_users").name == "archive_users"
    assert db.view_manager.get_view("archive.public", "active_users").name == "active_users"
    assert db.stored_procedure_manager.get_procedure("archive.public", "archive_users").name == "archive_users"

    db.drop_table_from_schema("store", "public", "users", cascade=True)

    with pytest.raises(ValueError, match="not found"):
        db.view_manager.get_view("store.public", "active_users")
    with pytest.raises(ValueError, match="not found"):
        db.stored_procedure_manager.get_procedure("store.public", "archive_users")
    assert db.view_manager.get_view("archive.public", "active_users").name == "active_users"
    assert db.stored_procedure_manager.get_procedure("archive.public", "archive_users").name == "archive_users"


def test_cascade_retains_legacy_unscoped_view_and_procedure_cleanup():
    db = manager()
    db.create_database("shop")
    db.create_table_in_schema("shop", "public", TableSchema("users", [ColumnSchema("id", "INT")]))
    db.provision_view("legacy", "users_view", "SELECT * FROM users", ["table:shop.public.users"])
    db.provision_view("legacy", "users_summary", "SELECT COUNT(*) FROM users", ["table:shop.public.users"])
    db.provision_view("legacy", "unrelated_view", "SELECT 1")
    db.provision_view("other_legacy", "other_unrelated_view", "SELECT 1")
    db.provision_procedure("legacy", "users_cleanup", [], "DELETE FROM users", ["table:shop.public.users"])

    db.drop_table_from_schema("shop", "public", "users", cascade=True)

    with pytest.raises(ValueError, match="not found"):
        db.view_manager.get_view("legacy", "users_view")
    with pytest.raises(ValueError, match="not found"):
        db.view_manager.get_view("legacy", "users_summary")
    assert db.view_manager.get_view("legacy", "unrelated_view").name == "unrelated_view"
    assert db.view_manager.get_view("other_legacy", "other_unrelated_view").name == "other_unrelated_view"
    with pytest.raises(ValueError, match="not found"):
        db.stored_procedure_manager.get_procedure("legacy", "users_cleanup")
