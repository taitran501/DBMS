from dbms.database_object.table import Table
from dbms.database_object.column import Column
from dbms.database_object.constraint import Constraint
from dbms.database_object.data_type import DataType
from dbms.database_object.index import Index
from dbms.database_object.partition import Partition
from dbms.database_object.row import Row
from unittest.mock import Mock


def test_table_can_be_created():
    columns = []
    rows = {}
    constraints = []
    indexes = []
    table = Table("t1", "users", columns, 0, rows, constraints, indexes)

    assert table.table_id == "t1"
    assert table.name == "users"
    assert table.columns is columns
    assert table.row_count == 0
    assert table.rows is rows
    assert table.constraints is constraints
    assert table.indexes is indexes
    assert callable(table.insert)
    assert callable(table.update)
    assert callable(table.delete)
    assert callable(table.truncate)
    assert callable(table.check_key_exists)


def test_insert():
    table = Table("t1", "users")
    row = Row("r1", {"name": "Alice"}, "v1")

    result = table.insert(row)

    assert result is True
    assert table.rows["r1"] is row
    assert table.row_count == 1


def test_update():
    row = Mock(spec=Row)
    row.update.return_value = True
    table = Table("t1", "users", rows={"r1": row}, row_count=1)
    new_values = {"name": "Bob"}

    result = table.update("r1", new_values)

    assert result is True
    row.update.assert_called_once_with(new_values)


def test_delete():
    row = Row("r1", {"name": "Alice"}, "v1")
    table = Table("t1", "users", rows={"r1": row}, row_count=1)

    result = table.delete("r1")

    assert result is True
    assert "r1" not in table.rows
    assert table.row_count == 0


def test_truncate():
    rows = {"r1": Row("r1", {"name": "Alice"}, "v1")}
    table = Table("t1", "users", rows=rows, row_count=1)

    result = table.truncate()

    assert result is True
    assert table.rows == {}
    assert table.row_count == 0


def test_check_key_exists():
    row = Row("r1", {"name": "Alice"}, "v1")
    table = Table("t1", "users", rows={"r1": row}, row_count=1)

    result = table.check_key_exists("r1")

    assert result is True


def test_add_column():
    column = Column("c1", "age", DataType("INT", lambda value: True, int))
    table = Table("t1", "users")

    result = table.add_column(column)

    assert result is True
    assert table.columns == [column]


def test_get_column():
    column = Column("c1", "age", DataType("INT", lambda value: True, int))
    table = Table("t1", "users", columns=[column])

    result = table.get_column("age")

    assert result is column


def test_rename_column():
    column = Column("c1", "age", DataType("INT", lambda value: True, int))
    table = Table("t1", "users", columns=[column])

    result = table.rename_column("age", "years")

    assert result is True
    assert column.name == "years"


def test_drop_column():
    column = Column("c1", "age", DataType("INT", lambda value: True, int))
    table = Table("t1", "users", columns=[column])

    result = table.drop_column("age")

    assert result is True
    assert table.columns == []


def test_add_constraint():
    constraint = Constraint("c1", "adult_only", "CHECK", lambda row: True)
    table = Table("t1", "users")

    result = table.add_constraint(constraint)

    assert result is True
    assert table.constraints == [constraint]


def test_drop_constraint():
    constraint = Constraint("c1", "adult_only", "CHECK", lambda row: True)
    table = Table("t1", "users", constraints=[constraint])

    result = table.drop_constraint("adult_only")

    assert result is True
    assert table.constraints == []


def test_add_index():
    index = Index("i1", "users_age", "B-Tree")
    table = Table("t1", "users")

    result = table.add_index(index)

    assert result is True
    assert table.indexes == [index]


def test_get_index():
    index = Index("i1", "users_age", "B-Tree")
    table = Table("t1", "users", indexes=[index])

    result = table.get_index("users_age")

    assert result is index


def test_drop_index():
    index = Index("i1", "users_age", "B-Tree")
    table = Table("t1", "users", indexes=[index])

    result = table.drop_index("users_age")

    assert result is True
    assert table.indexes == []


def test_add_partition():
    partition = Partition("p1", "part_1", (1, 100), object())
    table = Table("t1", "users")

    result = table.add_partition(partition)

    assert result is True
    assert table.partitions == [partition]


def test_get_partition():
    partition = Partition("p1", "part_1", (1, 100), object())
    table = Table("t1", "users", partitions=[partition])

    result = table.get_partition("part_1")

    assert result is partition


def test_drop_partition():
    partition = Partition("p1", "part_1", (1, 100), object())
    table = Table("t1", "users", partitions=[partition])

    result = table.drop_partition("part_1")

    assert result is True
    assert table.partitions == []
