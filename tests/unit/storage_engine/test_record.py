from dbms.storage_engine.record import Record


def test_record_stores_identifier_and_values():
    # Arrange / Act
    record = Record(1, {"name": "Ada"})

    # Assert
    assert record.record_id == 1
    assert record.values == {"name": "Ada"}
    assert callable(record.serialize)
    assert callable(record.deserialize)


def test_serialize_record():
    # Arrange
    record = Record(1, {"name": "Ada"})

    # Act
    result = record.serialize()

    # Assert
    assert isinstance(result, bytes)
    assert result


def test_deserialize_record():
    # Arrange
    original = Record(1, {"name": "Ada"})

    # Act
    result = Record.deserialize(original.serialize())

    # Assert
    assert result.record_id == original.record_id
    assert result.values == original.values
