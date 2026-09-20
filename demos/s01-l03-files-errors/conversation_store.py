from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from message_utils import normalize_message


class ConversationFileError(Exception):
    """对话文件存在但无法作为有效对话读取。"""


def save_messages(path: Path, messages: list[Any]) -> None:
    """清洗消息并将有效消息保存成 UTF-8 JSON 文件。"""
    cleaned_messages: list[dict[str, str]] = []

    for message in messages:
        normalized = normalize_message(message)
        if normalized is not None:
            cleaned_messages.append(normalized)

    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {"version": 1, "messages": cleaned_messages}
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
            

def load_messages(path: Path) -> list[dict[str, str]]:
    """读取并验证对话；文件不存在时返回空列表。"""
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError as e:
            raise ConversationFileError(f"无法解析 JSON 文件: {e}") from e

    # 新格式使用带版本号的字典；同时兼容旧版的消息列表。
    if isinstance(data, list):
        stored_messages = data
    elif isinstance(data, dict):
        if data.get("version") != 1:
            raise ConversationFileError("不支持的 version")
        stored_messages = data.get("messages")
        if not isinstance(stored_messages, list):
            raise ConversationFileError("messages 必须是列表")
    else:
        raise ConversationFileError("JSON 顶层必须是对象或旧版列表")

    result: list[dict[str, str]] = []
    for message in stored_messages:
        normalized = normalize_message(message)
        if normalized is not None:
            result.append(normalized)
    return result


def main() -> None:
    output_path = Path(__file__).with_name("data") / "conversation.json"
    messages = [
        {"role": "user", "content": "  什么是异常？  "},
        {"role": "assistant", "content": "异常表示程序运行时遇到了不能正常完成的情况。"},
        {"role": "user", "content": "   "},
    ]

    save_messages(output_path, messages)
    restored_messages = load_messages(output_path)
    print(f"已恢复 {len(restored_messages)} 条有效消息")
    print(restored_messages)


if __name__ == "__main__":
    main()
