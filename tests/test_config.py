from app.config import settings


def test_settings_load():
    assert hasattr(settings, "mongo_uri")
    assert hasattr(settings, "mongo_db_name")
    assert hasattr(settings, "openrouter_key")
    assert hasattr(settings, "openrouter_api_base")
    assert hasattr(settings, "openrouter_model")
    import os

    os.environ["MONGO_URI"] = "mongodb://test"
    refreshed = type(settings)()
    assert refreshed.mongo_uri == "mongodb://test"
