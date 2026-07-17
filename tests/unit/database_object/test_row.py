from dbms.database_object.row import Row


def test_row_can_be_created():
    row = Row("row1", [1, "Alice"], "v1")
    assert row.row_id == "row1"
    assert row.values == [1, "Alice"]
    assert row.version == "v1"


def test_read_row_values():
    row = Row("row1", [1, "Alice"], "v1")
    assert row.read() == [1, "Alice"]


def test_update_row_values():
    row = Row("row1", [1, "Alice"], "v1")
    assert row.update([1, "Bob"]) is True
    assert row.read() == [1, "Bob"]
