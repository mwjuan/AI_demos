from __future__ import annotations

import sys
from pathlib import Path

import pytest


LESSON_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LESSON_DIR))

from message_roles import SYSTEM_PROMPT, build_messages  # noqa: E402


def test_build_messages_adds_system_and_clean_user_message() -> None:
    assert build_messages("  什么是上下文？  ") == [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "什么是上下文？"},
    ]


@pytest.mark.parametrize("user_input", [None, 123, ["你好"]])
def test_build_messages_rejects_non_string_input(user_input: object) -> None:
    with pytest.raises(ValueError, match="字符串"):
        build_messages(user_input)


def test_build_messages_rejects_blank_input() -> None:
    with pytest.raises(ValueError, match="为空"):
        build_messages("  \n  ")
