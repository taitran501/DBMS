from dbms.administration_operations.import_export_manager import ImportExportManager


def test_import_export_manager_can_be_created():
    assert isinstance(ImportExportManager(), ImportExportManager)
