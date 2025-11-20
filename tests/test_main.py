def test_app_loads():
    from app.main import app
    assert app.title
    assert app.openapi_url
