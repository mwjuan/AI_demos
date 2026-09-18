import pytest

from week01_first_api.config import Config, load_config

PLACEHOLDER_KEY = "test-key"
OPENAI_PLACEHOLDER_KEY = f"sk-{PLACEHOLDER_KEY}"


def test_loads_deepseek_configuration() -> None:
    assert load_config(
        {
            "AI_PROVIDER": "deepseek",
            "DEEPSEEK_API_KEY": PLACEHOLDER_KEY,
            "DEEPSEEK_MODEL": "test-model",
            "DEEPSEEK_BASE_URL": "https://example.test/v1",
        }
    ) == Config(
        provider="deepseek",
        api_key=PLACEHOLDER_KEY,
        model="test-model",
        base_url="https://example.test/v1",
    )


def test_defaults_to_low_cost_deepseek_model() -> None:
    assert load_config({"DEEPSEEK_API_KEY": PLACEHOLDER_KEY}) == Config(
        provider="deepseek",
        api_key=PLACEHOLDER_KEY,
        model="deepseek-flash",
        base_url="https://api.deepseek.com",
    )


def test_can_switch_to_qwen() -> None:
    assert load_config(
        {"AI_PROVIDER": "qwen", "DASHSCOPE_API_KEY": PLACEHOLDER_KEY}
    ).provider == "qwen"


def test_can_switch_to_openai_and_override_defaults() -> None:
    assert load_config(
        {
            "AI_PROVIDER": "openai",
            "OPENAI_API_KEY": OPENAI_PLACEHOLDER_KEY,
            "OPENAI_MODEL": "custom-model",
            "OPENAI_BASE_URL": "https://example.test/v1",
        }
    ) == Config(
        provider="openai",
        api_key=OPENAI_PLACEHOLDER_KEY,
        model="custom-model",
        base_url="https://example.test/v1",
    )


def test_loads_optional_proxy() -> None:
    config = load_config(
        {
            "DEEPSEEK_API_KEY": PLACEHOLDER_KEY,
            "AI_PROXY_URL": "http://127.0.0.1:7897",
        }
    )
    assert config.proxy_url == "http://127.0.0.1:7897"


@pytest.mark.parametrize(
    ("env", "message"),
    [
        ({"AI_PROVIDER": "qwen"}, "DASHSCOPE_API_KEY"),
        (
            {"AI_PROVIDER": "openai", "OPENAI_API_KEY": "not-an-api-key"},
            "以 sk- 开头",
        ),
        ({"AI_PROVIDER": "unknown"}, "deepseek、qwen、openai"),
    ],
)
def test_rejects_invalid_configuration(env: dict[str, str], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        load_config(env)
