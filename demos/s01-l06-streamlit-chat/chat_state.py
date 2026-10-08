from __future__ import annotations

from typing import Any, MutableMapping


def initialize_messages(
    state: MutableMapping[str, Any],
) -> list[dict[str, str]]:
    """初始化并返回当前会话的消息列表。"""
    # messages 不存在时创建新列表；存在时直接返回原列表。
    if "messages" not in state:
        state["messages"] = []
    return state["messages"]

def reset_timeout(
    state: MutableMapping[str, Any],
) -> None:
    """重置当前会话的超时设置。"""
    state["timeout"] = 120
        

def clear_messages(
    state: MutableMapping[str, Any],
) -> list[dict[str, str]]:
    """清空当前会话的消息，并保留其他状态。"""
    # 只替换 messages，并返回新的空列表。
    messages: list[dict[str, str]] = []
    state['messages'] = messages

    return messages


def append_message(
    state: MutableMapping[str, Any],
    role: Any,
    content: Any,
) -> dict[str, str]:
    """验证并追加一条聊天消息。"""
    # 1. role 只能是 "user" 或 "assistant"。
    # 2. content 必须是非空字符串，并去除前后空白。
    # 3. 复用 initialize_messages(state) 获得消息列表。
    # 4. 追加并返回形如 {"role": role, "content": content} 的消息。
    if role not in ["user", "assistant"]:
        raise ValueError("role must be 'user' or 'assistant'.")

    if not isinstance(content, str) or not content.strip():
        raise ValueError("content must be a non-empty string.")
    messages = initialize_messages(state)
    message = {"role": role, "content": content.strip()}
    messages.append(message)
    return message