import pytest

from dbms.database_object.column import Column
from dbms.database_object.constraint import Constraint
from dbms.database_object.data_type import DataType
from dbms.database_object.index import Index
from dbms.database_object.table import Table
from dbms.database_object.table_builder import TableBuilder


def test_table_builder_basic_build():
    builder = TableBuilder("users", table_id="t1")
    table = builder.build()

    assert isinstance(table, Table)
    assert table.name == "users"
    assert table.table_id == "t1"
    assert table.columns == []
    assert table.constraints == []
    assert table.indexes == []


def test_table_builder_method_chaining_columns():
    table = (
        TableBuilder("users")
        .set_table_id("tbl_01")
        .add_column("id", "INT", nullable=False)
        .add_column("username", "VARCHAR")
        .build()
    )

    assert table.name == "users"
    assert table.table_id == "tbl_01"
    assert len(table.columns) == 2
    assert table.columns[0].name == "id"
    assert table.columns[0].nullable is False
    assert table.columns[1].name == "username"


def test_table_builder_add_column_object():
    col = Column("col_1", "email", DataType("VARCHAR", lambda v: True, str))
    table = TableBuilder("users").add_column_object(col).build()

    assert len(table.columns) == 1
    assert table.columns[0] is col


def test_table_builder_add_constraint_and_index():
    constraint = Constraint("c1", "pk_users", "PRIMARY KEY", object())
    index = Index("idx_1", "idx_users_id", "BTree")

    table = (
        TableBuilder("users")
        .add_column("id", "INT")
        .add_constraint(constraint)
        .add_index(index)
        .build()
    )

    assert table.constraints == [constraint]
    assert table.indexes == [index]


def test_table_builder_empty_name_raises_error():
    with pytest.raises(ValueError, match="Table name cannot be empty"):
        TableBuilder("")

    with pytest.raises(ValueError, match="Table name cannot be empty"):
        TableBuilder("   ")


def test_table_builder_duplicate_column_raises_error():
    builder = TableBuilder("users").add_column("id", "INT")

    with pytest.raises(ValueError, match="Column 'id' already exists"):
        builder.add_column("id", "VARCHAR")


def test_table_builder_rejects_empty_column_name():
    with pytest.raises(ValueError, match="Column name cannot be empty"):
        TableBuilder("users").add_column("", "INT")


def test_table_builder_rejects_empty_data_type_name():
    with pytest.raises(ValueError, match="Data type name cannot be empty"):
        TableBuilder("users").add_column("id", "")


def test_table_builder_maps_builtin_data_type_converter():
    table = TableBuilder("users").add_column("id", "int").build()

    assert table.columns[0].data_type.name == "INT"
    assert table.columns[0].data_type.converter("42") == 42


def test_table_builder_rejects_duplicate_constraint():
    constraint = Constraint("c1", "pk_users", "PRIMARY KEY", object())
    builder = TableBuilder("users").add_constraint(constraint)

    with pytest.raises(ValueError, match="Constraint 'pk_users' already exists"):
        builder.add_constraint(constraint)


def test_table_builder_rejects_duplicate_index():
    index = Index("idx_1", "idx_users_id", "BTree")
    builder = TableBuilder("users").add_index(index)

    with pytest.raises(ValueError, match="Index 'idx_users_id' already exists"):
        builder.add_index(index)


def test_built_table_does_not_share_builder_collections():
    builder = TableBuilder("users").add_column("id", "INT")
    table = builder.build()

    builder.add_column("email", "VARCHAR")

    assert [column.name for column in table.columns] == ["id"]


def test_separately_built_tables_do_not_share_collections():
    builder = TableBuilder("users").add_column("id", "INT")
    first_table = builder.build()
    second_table = builder.build()

    first_table.columns.append(Column("extra", "email", DataType("VARCHAR", lambda v: True, str)))

    assert [column.name for column in second_table.columns] == ["id"]
