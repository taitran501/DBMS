from dbms.database_object.row import Row


def test_row_can_be_created():
    # Arrange
    row = Row("row1", [1, "Alice"], "v1")

    # Assert
    assert row.row_id == "row1"
    assert row.values == [1, "Alice"]
    assert row.version == "v1"
    assert callable(row.read)
    assert callable(row.update)


def test_read():
    # Arrange
    values = [1, "Alice"]
    row = Row("row1", values, "v1")

    # Act
    result = row.read()

    # Assert
    assert result is values


def test_update():
    # Arrange
    row = Row("row1", [1, "Alice"], "v1")
    new_values = [1, "Bob"]

    # Act
    result = row.update(new_values)

    # Assert
    assert result is True
    assert row.values is new_values
