from papercoach.config import Settings
from papercoach.services.llm import build_llm_client


def test_local_provider_builds_no_llm_client(tmp_path) -> None:
    settings = Settings(data_dir=tmp_path, llm_provider="local")

    assert build_llm_client(settings) is None


def test_deepseek_provider_uses_configured_model_without_exposing_key(tmp_path) -> None:
    settings = Settings(
        data_dir=tmp_path,
        llm_provider="deepseek",
        deepseek_api_key="sk-test",
        deepseek_model="deepseek-v4-pro",
    )

    client = build_llm_client(settings)

    assert client is not None
    assert client.provider == "deepseek"
    assert client.model == "deepseek-v4-pro"
    assert client.base_url == "https://api.deepseek.com"
