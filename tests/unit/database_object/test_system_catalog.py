from dbms.database_object.system_catalog import SystemCatalog


def test_system_catalog_returns_placeholder_results():
    catalog = SystemCatalog()

    assert catalog.register("users", object()) is True
    assert catalog.find("users") is None
    assert catalog.remove("users") is True
