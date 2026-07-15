from datetime import date, datetime
from decimal import Decimal

import pytest

from dbms.database_object.column_management import Column
from dbms.database_object.data_type_management import DataTypeManager
from dbms.database_object.database_management import DatabaseConfiguration, DatabaseManager
from dbms.database_object.index_management import Index, IndexAccessMethod, IndexManager
from dbms.database_object.metadata_management import MetadataManager
from dbms.database_object.schema_management import SchemaManager
from dbms.database_object.schema_management.schema import ColumnSchema, TableSchema
from dbms.database_object.table_management import TableManager


def test_database_configuration_validates_runtime_settings_and_database_can_be_renamed():
    manager = DatabaseManager()
    config = DatabaseConfiguration(
        page_size=8192,
        encoding="utf-8",
        max_size_mb=32,
        storage_location="C:\\db-data\\shop",
        default_schema="public",
    )

    database = manager.create_database("shop", config)
    renamed = manager.rename_database("shop", "store")

    assert database is renamed
    assert manager.get_database("store").descriptor.config.default_schema == "public"
    assert manager._registry.find_database_by_name("shop") is None
    with pytest.raises(ValueError, match="absolute"):
        manager.create_database("relative", DatabaseConfiguration(storage_location="data"))
    with pytest.raises(ValueError, match="encoding"):
        manager.create_database("bad_encoding", DatabaseConfiguration(encoding="not-a-codec"))
    with pytest.raises(ValueError, match="max size"):
        manager.create_database("bad_quota", DatabaseConfiguration(max_size_mb=0))


def test_schema_rename_preserves_owner_and_exposes_migration_history():
    schemas = SchemaManager()
    schemas.create_schema("shop", "public")
    schemas.change_schema_owner("shop", "public", "alice")

    schemas.rename_schema("shop", "public", "app")

    assert schemas.get_schema("shop", "app").name == "app"
    assert schemas.owners[("shop", "app")] == "alice"
    assert any("Renamed" in item for item in schemas.get_schema_migration_history("app"))


def test_table_and_column_rename_update_schema_rows_and_column_catalog():
    tables = TableManager()
    table = tables.create_table("shop.public", "users", TableSchema("users", [ColumnSchema("id", "INT"), ColumnSchema("name", "TEXT")]))
    tables.insert_row(table, {"id": 1, "name": "Ada"})

    tables.rename_column(table, "name", "display_name")
    tables.rename_table("shop.public", "users", "members")

    renamed = tables.get_table("shop.public", "members")
    assert renamed.schema.name == "members"
    assert renamed.schema.column_names() == ["id", "display_name"]
    assert renamed.rows[1] == {"id": 1, "display_name": "Ada"}


def test_metadata_can_list_scoped_objects_and_rename_dependency_keys():
    metadata = MetadataManager()
    metadata.register_metadata("table", "shop.public.users", object())
    metadata.register_metadata("view", "shop.public.active_users", object(), ["table:shop.public.users"])

    metadata.rename_metadata("table", "shop.public.users", "shop.public.members")

    assert metadata.list_metadata("table", "shop.public") == ("shop.public.members",)
    assert metadata.dependency_manager.get_metadata_dependencies("view:shop.public.active_users") == ("table:shop.public.members",)


def test_index_rebuild_and_extended_types_have_explicit_contracts():
    indexes = IndexManager()
    index = Index("users_email", IndexAccessMethod.HASH, ["email"], unique=True)
    indexes.create_index("shop.public.users", index)
    indexes.rebuild_index("shop.public.users", "users_email", ((1, {"email": "a"}), (2, {"email": "b"})))
    indexes.rebuild_index("shop.public.users", "users_email", ())

    assert indexes.find_indexed_row_ids("shop.public.users", "users_email", ("a",)) == ()
    with pytest.raises(ValueError, match="B_TREE"):
        indexes.find_indexed_row_ids_in_range("shop.public.users", "users_email")

    types = DataTypeManager()
    types.register_type(types.make_descriptor("DECIMAL"))
    types.register_type(types.make_descriptor("DATE"))
    types.register_type(types.make_descriptor("DATETIME"))
    assert types.convert_value(types.resolve("DECIMAL"), "1.50") == Decimal("1.50")
    assert types.validate_value(types.resolve("DATE"), date.today()) is True
    assert types.validate_value(types.resolve("DATETIME"), datetime.now()) is True
    varchar = types.register_type(types.make_descriptor("VARCHAR", length=3))
    assert types.validate_value(varchar, "abc") is True
    assert types.validate_value(varchar, "long") is False
