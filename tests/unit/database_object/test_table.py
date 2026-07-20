from unittest.mock import Mock
import pytest

from dbms.database_object.table import Table
from dbms.database_object.column import Column
from dbms.database_object.constraint import Constraint
from dbms.database_object.data_type import DataType
from dbms.database_object.index import Index
from dbms.database_object.partition import Partition
from dbms.database_object.row import Row


def test_table_can_be_created():
    # Arrange
    columns = []
    rows = {}
    constraints = []
    indexes = []
    table = Table("t1", "users", columns, 0, rows, constraints, indexes)

    # Assert
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
    # Arrange
    table = Table("t1", "users")
    row = Row("r1", {"name": "Alice"}, "v1")

    # Act
    result = table.insert(row)

    # Assert
    assert result is True
    assert table.rows["r1"] is row
    assert table.row_count == 1


def test_update():
    # Arrange
    row = Mock(spec=Row)
    row.update.return_value = True
    table = Table("t1", "users", rows={"r1": row}, row_count=1)
    new_values = {"name": "Bob"}

    # Act
    result = table.update("r1", new_values)

    # Assert
    assert result is True
    row.update.assert_called_once_with(new_values)


def test_delete():
    # Arrange
    row = Row("r1", {"name": "Alice"}, "v1")
    table = Table("t1", "users", rows={"r1": row}, row_count=1)

    # Act
    result = table.delete("r1")

    # Assert
    assert result is True
    assert "r1" not in table.rows
    assert table.row_count == 0


def test_truncate():
    # Arrange
    rows = {"r1": Row("r1", {"name": "Alice"}, "v1")}
    table = Table("t1", "users", rows=rows, row_count=1)

    # Act
    result = table.truncate()

    # Assert
    assert result is True
    assert table.rows == {}
    assert table.row_count == 0


def test_check_key_exists():
    # Arrange
    row = Row("r1", {"name": "Alice"}, "v1")
    table = Table("t1", "users", rows={"r1": row}, row_count=1)

    # Act
    result = table.check_key_exists("r1")

    # Assert
    assert result is True


def test_add_column():
    # Arrange
    column = Column("c1", "age", DataType("INT", lambda value: True, int))
    table = Table("t1", "users")

    # Act
    result = table.add_column(column)

    # Assert
    assert result is True
    assert table.columns == [column]


def test_get_column():
    # Arrange
    column = Column("c1", "age", DataType("INT", lambda value: True, int))
    table = Table("t1", "users", columns=[column])

    # Act
    result = table.get_column("age")

    # Assert
    assert result is column


def test_rename_column():
    # Arrange
    column = Column("c1", "age", DataType("INT", lambda value: True, int))
    table = Table("t1", "users", columns=[column])

    # Act
    result = table.rename_column("age", "years")

    # Assert
    assert result is True
    assert column.name == "years"


def test_drop_column():
    # Arrange
    column = Column("c1", "age", DataType("INT", lambda value: True, int))
    table = Table("t1", "users", columns=[column])

    # Act
    result = table.drop_column("age")

    # Assert
    assert result is True
    assert table.columns == []


def test_add_constraint():
    # Arrange
    constraint = Constraint("c1", "adult_only", "CHECK", lambda row: True)
    table = Table("t1", "users")

    # Act
    result = table.add_constraint(constraint)

    # Assert
    assert result is True
    assert table.constraints == [constraint]


def test_drop_constraint():
    # Arrange
    constraint = Constraint("c1", "adult_only", "CHECK", lambda row: True)
    table = Table("t1", "users", constraints=[constraint])

    # Act
    result = table.drop_constraint("adult_only")

    # Assert
    assert result is True
    assert table.constraints == []


def test_add_index():
    # Arrange
    index = Index("i1", "users_age", "B-Tree")
    table = Table("t1", "users")

    # Act
    result = table.add_index(index)

    # Assert
    assert result is True
    assert table.indexes == [index]


def test_get_index():
    # Arrange
    index = Index("i1", "users_age", "B-Tree")
    table = Table("t1", "users", indexes=[index])

    # Act
    result = table.get_index("users_age")

    # Assert
    assert result is index


def test_drop_index():
    # Arrange
    index = Index("i1", "users_age", "B-Tree")
    table = Table("t1", "users", indexes=[index])

    # Act
    result = table.drop_index("users_age")

    # Assert
    assert result is True
    assert table.indexes == []


def test_add_partition():
    # Arrange
    partition = Partition("p1", "part_1", (1, 100), object())
    table = Table("t1", "users")

    # Act
    result = table.add_partition(partition)

    # Assert
    assert result is True
    assert table.partitions == [partition]


def test_get_partition():
    # Arrange
    partition = Partition("p1", "part_1", (1, 100), object())
    table = Table("t1", "users", partitions=[partition])

    # Act
    result = table.get_partition("part_1")

    # Assert
    assert result is partition


def test_drop_partition():
    # Arrange
    partition = Partition("p1", "part_1", (1, 100), object())
    table = Table("t1", "users", partitions=[partition])

    # Act
    result = table.drop_partition("part_1")

    # Assert
    assert result is True
    assert table.partitions == []


def test_insert_duplicate_row_id():
    # Arrange: Setup table with existing row 'r1'
    existing_row = Row("r1", {"name": "Alice"}, "v1")
    table = Table("t1", "users", rows={"r1": existing_row}, row_count=1)
    duplicate_row = Row("r1", {"name": "Bob"}, "v1")

    # Act & Assert: Inserting row with duplicate row_id 'r1' should raise ValueError
    with pytest.raises(ValueError):
        table.insert(duplicate_row)


def test_update_unknown_row():
    # Arrange: Setup table with empty rows
    table = Table("t1", "users", rows={}, row_count=0)

    # Act & Assert: Updating a non-existent row should raise KeyError
    with pytest.raises(KeyError):
        table.update("non_existent_row", {"name": "Bob"})


def test_delete_unknown_row():
    # Arrange: Setup table with empty rows
    table = Table("t1", "users", rows={}, row_count=0)

    # Act & Assert: Deleting a non-existent row should raise KeyError
    with pytest.raises(KeyError):
        table.delete("non_existent_row")


def test_add_duplicate_column():
    # Arrange: Setup table with existing column 'age'
    col1 = Column("c1", "age", DataType("INT", lambda v: True, int))
    table = Table("t1", "users", columns=[col1])
    col2 = Column("c2", "age", DataType("INT", lambda v: True, int))

    # Act & Assert: Adding a column with duplicate name 'age' should raise ValueError
    with pytest.raises(ValueError):
        table.add_column(col2)


def test_get_unknown_column():
    # Arrange: Setup table with no columns
    table = Table("t1", "users", columns=[])

    # Act & Assert: Getting a non-existent column should raise KeyError
    with pytest.raises(KeyError):
        table.get_column("non_existent_column")


def test_drop_unknown_column():
    # Arrange: Setup table with no columns
    table = Table("t1", "users", columns=[])

    # Act & Assert: Dropping a non-existent column should raise KeyError
    with pytest.raises(KeyError):
        table.drop_column("non_existent_column")
