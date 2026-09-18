from __future__ import annotations

import httpx
from openai import OpenAI

from .config import Config


def create_model_client(config: Config) -> OpenAI:
    """根据统一配置创建模型客户端；仅在配置后才使用代理。"""
    http_client = httpx.Client(proxy=config.proxy_url) if config.proxy_url else None
    return OpenAI(
        api_key=config.api_key,
        base_url=config.base_url,
        http_client=http_client,
    )

