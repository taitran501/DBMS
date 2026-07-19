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


def test_delete_row():
    # Deletion is represented as row state so later version logic can observe it.
    row = Row("row1", {"name": "Ada"}, "v1")

    assert row.delete() is True
    assert row.is_deleted is True


def test_clone_version():
    # A new version keeps the logical row identity but is a separate Row object.
    row = Row("row1", {"name": "Ada"}, "v1")

    clone = row.clone_version("v2")

    assert clone is not row
    assert clone.values == row.values
    assert clone.version == "v2"


def test_restore_version():
    # Restoring copies the snapshot values and version back to the live row.
    row = Row("row1", {"name": "Grace"}, "v2")
    snapshot = Row("row1", {"name": "Ada"}, "v1")

    assert row.restore_version(snapshot) is True
    assert row.values == {"name": "Ada"}
    assert row.version == "v1"


def test_compare_rows():
    # Row equality includes identity, values, and version rather than values alone.
    row = Row("row1", {"name": "Ada"}, "v1")

    assert row.compare(Row("row1", {"name": "Ada"}, "v1")) is True
    assert row.compare(Row("row2", {"name": "Grace"}, "v1")) is False


def test_serialize():
    # Serialization produces a stable payload containing the row's persisted fields.
    row = Row("row1", {"name": "Ada"}, "v1")

    assert row.serialize() == '{"row_id":"row1","values":{"name":"Ada"},"version":"v1"}'


def test_deserialize():
    # Deserialization reconstructs the same identity, values, and version.
    row = Row.deserialize('{"row_id":"row1","values":{"name":"Ada"},"version":"v1"}')

    assert row.row_id == "row1"
    assert row.values == {"name": "Ada"}
    assert row.version == "v1"
