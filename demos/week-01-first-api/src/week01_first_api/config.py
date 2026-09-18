from __future__ import annotations

from dataclasses import dataclass
from os import environ
from typing import Mapping


@dataclass(frozen=True)
class ProviderSettings:
    key_name: str
    model_name: str
    base_url_name: str
    default_model: str
    default_base_url: str


@dataclass(frozen=True)
class Config:
    provider: str
    api_key: str
    model: str
    base_url: str
    proxy_url: str | None = None


PROVIDERS = {
    "deepseek": ProviderSettings(
        key_name="DEEPSEEK_API_KEY",
        model_name="DEEPSEEK_MODEL",
        base_url_name="DEEPSEEK_BASE_URL",
        default_model="deepseek-flash",
        default_base_url="https://api.deepseek.com",
    ),
    "qwen": ProviderSettings(
        key_name="DASHSCOPE_API_KEY",
        model_name="QWEN_MODEL",
        base_url_name="QWEN_BASE_URL",
        default_model="qwen-plus",
        default_base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    ),
    "openai": ProviderSettings(
        key_name="OPENAI_API_KEY",
        model_name="OPENAI_MODEL",
        base_url_name="OPENAI_BASE_URL",
        default_model="gpt-5.6-luna",
        default_base_url="https://api.openai.com/v1",
    ),
}


def _value(env: Mapping[str, str], name: str) -> str | None:
    value = env.get(name)
    return value.strip() if value and value.strip() else None


def load_config(env: Mapping[str, str] | None = None) -> Config:
    values = environ if env is None else env
    provider = (_value(values, "AI_PROVIDER") or "deepseek").lower()
    settings = PROVIDERS.get(provider)

    if settings is None:
        raise ValueError(
            f"不支持 AI_PROVIDER={provider}。当前可选值：deepseek、qwen、openai。"
        )

    api_key = _value(values, settings.key_name)
    if not api_key or api_key.startswith("replace_with_"):
        raise ValueError(
            f"当前提供商是 {provider}，但缺少 {settings.key_name}。"
            "请在 .env 中填入有效密钥。"
        )

    if provider == "openai" and not api_key.startswith("sk-"):
        raise ValueError(
            "OPENAI_API_KEY 格式不正确。请使用 OpenAI Platform 创建的、"
            "以 sk- 开头的 Secret API key；ChatGPT/Codex 登录令牌不能用于 API。"
        )

    return Config(
        provider=provider,
        api_key=api_key,
        model=_value(values, settings.model_name) or settings.default_model,
        base_url=_value(values, settings.base_url_name) or settings.default_base_url,
        proxy_url=_value(values, "AI_PROXY_URL"),
    )

