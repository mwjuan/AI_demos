from __future__ import annotations

import sys
from pathlib import Path

import pytest


LESSON_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LESSON_DIR))

from chat_state import (  # noqa: E402
    append_message,
    clear_messages,
    initialize_messages,
)


def test_initialize_messages_creates_empty_list() -> None:
    state: dict[str, object] = {}

    messages = initialize_messages(state)

    assert messages == []
    assert state["messages"] is messages


def test_initialize_messages_preserves_existing_messages() -> None:
    existing = [{"role": "user", "content": "你好"}]
    state: dict[str, object] = {"messages": existing}

    messages = initialize_messages(state)

    assert messages is existing


def test_initialize_messages_does_not_share_lists_between_sessions() -> None:
    first_state: dict[str, object] = {}
    second_state: dict[str, object] = {}

    first_messages = initialize_messages(first_state)
    second_messages = initialize_messages(second_state)
    first_messages.append({"role": "user", "content": "只属于第一个会话"})

    assert second_messages == []
    assert first_messages is not second_messages


def test_clear_messages_only_clears_chat_history() -> None:
    state: dict[str, object] = {
        "messages": [{"role": "user", "content": "你好"}],
        "model": "qwen3:4b",
        "temperature": 0.2,
    }

    messages = clear_messages(state)

    assert messages == []
    assert state["messages"] is messages
    assert state["model"] == "qwen3:4b"
    assert state["temperature"] == 0.2


def test_append_message_preserves_order_and_cleans_content() -> None:
    state: dict[str, object] = {}

    first = append_message(state, "user", "  解释 Token  ")
    second = append_message(state, "assistant", "Token 是文本单位。")

    assert first == {"role": "user", "content": "解释 Token"}
    assert second == {"role": "assistant", "content": "Token 是文本单位。"}
    assert state["messages"] == [first, second]


@pytest.mark.parametrize("role", [None, "", "system", "tool", 123])
def test_append_message_rejects_invalid_role(role: object) -> None:
    with pytest.raises(ValueError, match="role"):
        append_message({}, role, "解释 Token")


@pytest.mark.parametrize("content", [None, "", "   ", ["解释 Token"]])
def test_append_message_rejects_invalid_content(content: object) -> None:
    with pytest.raises(ValueError, match="content"):
        append_message({}, "user", content)
