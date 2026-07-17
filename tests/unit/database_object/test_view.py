from dbms.database_object.view import View


def test_view_can_be_created():
    query_executor = object()
    cached_results = []
    view = View("v1", "active_users", "SELECT * FROM users", query_executor, cached_results)

    assert view.view_id == "v1"
    assert view.name == "active_users"
    assert view.query_definition == "SELECT * FROM users"
    assert view.query_executor is query_executor
    assert view.cached_results is cached_results
    assert callable(view.create_view)
    assert callable(view.refresh)


def test_create_view():
    pass


def test_refresh():
    pass
