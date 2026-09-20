from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


LESSON_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LESSON_DIR))

from conversation_store import (  # noqa: E402
    ConversationFileError,
    load_messages,
    save_messages,
)


def test_save_messages_writes_clean_utf8_json(tmp_path: Path) -> None:
    output_path = tmp_path / "nested" / "conversation.json"

    save_messages(
        output_path,
        [
            {"role": "user", "content": "  你好  "},
            {"role": "assistant", "content": "欢迎学习文件操作"},
            {"role": "user", "content": "   "},
        ],
    )

    assert json.loads(output_path.read_text(encoding="utf-8")) == {
            "version": 1,
            "messages": [
                {"role": "user", "content": "你好"},
                {"role": "assistant", "content": "欢迎学习文件操作"},
            ],
        }
    assert "你好" in output_path.read_text(encoding="utf-8")


def test_load_messages_returns_empty_list_for_missing_file(tmp_path: Path) -> None:
    assert load_messages(tmp_path / "missing.json") == []


def test_load_messages_restores_and_cleans_messages(tmp_path: Path) -> None:
    input_path = tmp_path / "conversation.json"
    input_path.write_text(
        json.dumps({
            "version": 1,
            "messages":  [
                {"role": "user", "content": "  Token 是什么？  "},
                {"role": "assistant", "content": "模型处理文本的基本单位"},
            ],
        },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    assert load_messages(input_path) ==  [
            {"role": "user", "content": "Token 是什么？"},
            {"role": "assistant", "content": "模型处理文本的基本单位"},
        ]


def test_load_messages_rejects_broken_json(tmp_path: Path) -> None:
    input_path = tmp_path / "broken.json"
    input_path.write_text('[{"role": "user"}', encoding="utf-8")

    with pytest.raises(ConversationFileError, match="JSON"):
        load_messages(input_path)


def test_load_messages_rejects_non_list_messages(tmp_path: Path) -> None:
    input_path = tmp_path / "object.json"
    input_path.write_text('{"version": 1, "messages": {}}', encoding="utf-8")

    with pytest.raises(ConversationFileError, match="messages.*列表"):
        load_messages(input_path)


def test_load_messages_rejects_unknown_version(tmp_path: Path) -> None:
    input_path = tmp_path / "conversation.json"
    input_path.write_text('{"version": 2, "messages": []}', encoding="utf-8")
    
    with pytest.raises(ConversationFileError, match="version"):
        load_messages(input_path)
        
def test_load_messages_reads_versioned_format(tmp_path: Path) -> None:
    input_path = tmp_path / "conversation.json"
    input_path.write_text(
        '{"version": 1, "messages": []}',
        encoding="utf-8",
    )

    assert load_messages(input_path) == []
