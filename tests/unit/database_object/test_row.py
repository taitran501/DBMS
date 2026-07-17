from dbms.database_object.row import Row


def test_row_can_be_created():
    row = Row("row1", [1, "Alice"], "v1")

    assert row.row_id == "row1"
    assert row.values == [1, "Alice"]
    assert row.version == "v1"
    assert callable(row.read)
    assert callable(row.update)


def test_read():
    values = [1, "Alice"]
    row = Row("row1", values, "v1")

    result = row.read()

    assert result is values


def test_update():
    row = Row("row1", [1, "Alice"], "v1")
    new_values = [1, "Bob"]

    result = row.update(new_values)

    assert result is True
    assert row.values is new_values
