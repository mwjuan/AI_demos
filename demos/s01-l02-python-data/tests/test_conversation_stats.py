from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).resolve().parents[1] / "conversation_stats.py"
SPEC = importlib.util.spec_from_file_location("conversation_stats", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
conversation_stats = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(conversation_stats)

normalize_message = conversation_stats.normalize_message
summarize_messages = conversation_stats.summarize_messages


def test_normalize_message_strips_content() -> None:
    assert normalize_message({"role": "user", "content": "  你好  "}) == {
        "role": "user",
        "content": "你好",
    }


def test_normalize_message_ignores_blank_content() -> None:
    assert normalize_message({"role": "assistant", "content": " \n  "}) is None


@pytest.mark.parametrize(
    "message",
    [
        "不是字典",
        {"role": "system", "content": "暂不支持的角色"},
        {"role": "user", "content": 123},
        {"role": "user"},
    ],
)
def test_normalize_message_rejects_invalid_input(message: object) -> None:
    with pytest.raises(ValueError):
        normalize_message(message)


def test_summarize_messages_counts_valid_messages() -> None:
    result = summarize_messages(
        [
            {"role": "user", "content": "  你好  "},
            {"role": "assistant", "content": "你好，有什么可以帮你？"},
            {"role": "user", "content": "   "},
            {"role": "user", "content": "解释 Token"},
        ]
    )

    assert result == {
        "message_count": 3,
        "role_counts": {"user": 2, "assistant": 1},
        "total_chars": 21,
        "longest_message": "你好，有什么可以帮你？",
        "average_chars": 7.0,
    }


def test_summarize_messages_handles_empty_list() -> None:
    assert summarize_messages([]) == {
        "message_count": 0,
        "role_counts": {"user": 0, "assistant": 0},
        "total_chars": 0,
        "longest_message": "",
        "average_chars": 0.0,
    }


def test_summarize_messages_rounds_average_to_one_decimal() -> None:
    result = summarize_messages(
        [
            {"role": "user", "content": "甲"},
            {"role": "assistant", "content": "乙"},
            {"role": "user", "content": "丙丁"},
        ]
    )

    assert result["average_chars"] == 1.3

