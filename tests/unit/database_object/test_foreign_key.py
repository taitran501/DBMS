from dbms.database_object.foreign_key import ForeignKey
from dbms.database_object.table import Table
from unittest.mock import Mock


def test_foreign_key_can_be_created():
    reference_table = object()
    foreign_key = ForeignKey("fk1", reference_table, "id", "restrict", "cascade")

    assert foreign_key.constraint_id == "fk1"
    assert foreign_key.reference_table is reference_table
    assert foreign_key.reference_column == "id"
    assert foreign_key.on_delete == "restrict"
    assert foreign_key.on_update == "cascade"
    assert callable(foreign_key.validate_reference)


def test_validate_reference():
    reference_table = Mock(spec=Table)
    reference_table.check_key_exists.return_value = True
    foreign_key = ForeignKey("fk1", reference_table, "id", "restrict", "cascade")

    result = foreign_key.validate_reference(10)

    assert result is True
    reference_table.check_key_exists.assert_called_once_with(10)
