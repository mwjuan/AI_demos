from __future__ import annotations

from typing import Any


def normalize_message(message: Any) -> dict[str, str] | None:
    """验证并清洗一条消息；空消息返回 None。"""
    if not isinstance(message, dict):
        raise ValueError("message 必须是字典")

    role = message.get("role")
    content = message.get("content")

    if role not in {"user", "assistant"}:
        raise ValueError("role 必须是 'user' 或 'assistant'")
    if not isinstance(content, str):
        raise ValueError("content 必须是字符串")

    cleaned_content = content.strip()
    if not cleaned_content:
        return None

    return {"role": role, "content": cleaned_content}
