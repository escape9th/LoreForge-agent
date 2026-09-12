from loreforge.config import Settings


def test_settings_reads_openai_compatible_environment(monkeypatch):
    monkeypatch.setenv("LOREFORGE_MODEL_ENDPOINT", "https://model.test/v1/chat")
    monkeypatch.setenv("LOREFORGE_MODEL_API_KEY", "secret")
    monkeypatch.setenv("LOREFORGE_MODEL_NAME", "small-model")

    settings = Settings.from_env()

    assert settings.model_endpoint == "https://model.test/v1/chat"
    assert settings.model_api_key == "secret"
    assert settings.model_name == "small-model"


def test_settings_defaults_to_demo_provider(monkeypatch):
    monkeypatch.delenv("LOREFORGE_MODEL_ENDPOINT", raising=False)
    monkeypatch.delenv("LOREFORGE_MODEL_API_KEY", raising=False)
    monkeypatch.delenv("LOREFORGE_MODEL_NAME", raising=False)

    settings = Settings.from_env()

    assert settings.use_demo_model is True
