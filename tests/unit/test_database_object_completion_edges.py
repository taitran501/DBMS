from datetime import date, datetime
from decimal import Decimal

import pytest

from dbms.database_object.column_management import Column, ColumnManager
from dbms.database_object.constraint_management import Constraint, ConstraintManager
from dbms.database_object.data_type_management import DataTypeManager, TypeConverter
from dbms.database_object.database_management import DatabaseConfiguration, DatabaseManager
from dbms.database_object.index_management import Index, IndexManager
from dbms.database_object.metadata_management import MetadataManager
from dbms.database_object.relationship_management import ReferentialActionPolicy, Relationship, RelationshipManager
from dbms.database_object.schema_management import SchemaManager
from dbms.database_object.schema_management.schema import ColumnSchema, TableSchema
from dbms.database_object.table_management import TableManager
from dbms.errors import DependencyExistsError
from dbms.subsystems import DatabaseObjectManager


def test_new_configuration_and_type_contracts_cover_invalid_and_boundary_values():
    databases = DatabaseManager()
    with pytest.raises(ValueError, match="name"):
        databases.create_database(" ")
    with pytest.raises(ValueError, match="Default schema"):
        databases.create_database("shop", DatabaseConfiguration(default_schema=""))
    databases.create_database("shop")
    databases.create_database("other")
    with pytest.raises(ValueError, match="already exists"):
        databases.rename_database("shop", "other")
    databases.drop_database("missing")

    converter = TypeConverter()
    assert converter.convert_type_value("FLOAT", "bad") == "bad"
    assert converter.convert_type_value("DECIMAL", "bad") == "bad"
    assert converter.convert_type_value("DATE", "bad") == "bad"
    assert converter.convert_type_value("DATETIME", "bad") == "bad"

    types = DataTypeManager()
    decimal = types.register_type(types.make_descriptor("DECIMAL", precision=3, scale=1))
    assert types.validate_value(decimal, Decimal("12.3")) is True
    assert types.validate_value(decimal, Decimal("12.34")) is False
    assert types.make_descriptor("CUSTOM").python_type is object
    for name, value in (("FLOAT", 1.5), ("DATE", date.today()), ("DATETIME", datetime.now())):
        item = types.register_type(types.make_descriptor(name))
        assert types.validate_value(item, value) is True


def test_low_level_rename_helpers_reject_conflicts_and_update_all_relationship_sides():
    columns = ColumnManager()
    columns.rename_table("missing", "other")
    columns.add_column("t", Column("old", "INT"))
    columns.add_column("t", Column("taken", "INT"))
    with pytest.raises(ValueError, match="already exists"):
        columns.rename_column("t", "old", "taken")

    constraints = ConstraintManager()
    constraints.rename_table("missing", "other")
    constraints.create_constraint("t", Constraint("c", "CHECK", ["old"]))
    constraints.rename_table("t", "u")
    constraints.rename_column("u", "old", "new")
    assert constraints.get_constraint("u", "c").columns == ["new"]

    relationships = RelationshipManager()
    relationship = Relationship("r", "source", "target", "FOREIGN_KEY", ReferentialActionPolicy(), ["old"], ["old"])
    relationships.create_relationship(relationship)
    relationships.rename_table("source", "new_source")
    relationships.rename_table("target", "new_target")
    relationships.rename_column("new_source", "old", "source_id")
    relationships.rename_column("new_target", "old", "target_id")
    assert relationship.descriptor.source_columns == ("source_id",)
    assert relationship.descriptor.target_columns == ("target_id",)


def test_metadata_schema_and_table_failure_paths_have_explicit_results():
    metadata = MetadataManager()
    metadata.register_metadata("table", "one", object())
    metadata.register_metadata("table", "two", object())
    assert metadata.list_metadata("table") == ("one", "two")
    with pytest.raises(ValueError, match="not found"):
        metadata.rename_metadata("table", "missing", "new")
    with pytest.raises(ValueError, match="already exists"):
        metadata.rename_metadata("table", "one", "two")
    metadata.rename_metadata_scope("does_not_match", "ignored")

    schemas = SchemaManager()
    schemas.create_schema("shop", "public")
    schemas.create_schema("other", "public")
    with pytest.raises(ValueError, match="already has schemas"):
        schemas.rename_database_scope("shop", "other")
    with pytest.raises(ValueError, match="already exists"):
        schemas.rename_schema("shop", "public", "public")

    tables = TableManager()
    table = tables.create_table("s", "t", TableSchema("t", [ColumnSchema("id", "INT")]))
    with pytest.raises(ValueError, match="already exists"):
        tables.rename_table("s", "t", "t")
    with pytest.raises(ValueError, match="already exists"):
        tables.rename_column(table, "id", "id")


def test_coordinator_rejects_invalid_definitions_and_restricts_database_drop():
    db = DatabaseObjectManager(MetadataManager().catalog, IndexManager())
    db.create_database("shop")
    db.create_table_in_schema("shop", "public", TableSchema("parents", [ColumnSchema("id", "INT")]))
    db.create_table_in_schema("shop", "public", TableSchema("children", [ColumnSchema("parent_id", "INT")]))

    db.create_index("legacy", "parents", "id")
    with pytest.raises(ValueError, match="unknown column"):
        db.create_index_for_table("shop", "public", "parents", Index("bad", "HASH", ["missing"]))
    with pytest.raises(ValueError, match="unknown column"):
        db.create_constraint_for_table("shop", "public", "parents", Constraint("bad", "CHECK", ["missing"]))
    with pytest.raises(ValueError, match="unknown column"):
        db.create_relationship(Relationship("bad", "shop.public.children", "shop.public.parents", "FOREIGN_KEY", ReferentialActionPolicy(), ["missing"], ["id"]))
    with pytest.raises(DependencyExistsError):
        db.drop_database("shop")

    bare = DatabaseObjectManager(MetadataManager().catalog, IndexManager())
    bare.database_manager.create_database("bare")
    bare.drop_database("bare", cascade=True)

    IndexManager().rename_table("missing", "still_missing")
    with_metadata = DatabaseObjectManager(MetadataManager().catalog, IndexManager())
    with_metadata.create_database("with_metadata")
    with_metadata.drop_database("with_metadata", cascade=True)
