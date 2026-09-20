from __future__ import annotations

from typing import Any


SYSTEM_PROMPT = (
    "你是一名耐心的 AI 学习助手。"
    "使用简洁的中文回答；不确定时要明确说明。"
)

SAMPLE_CONVERSATION = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": "Token 是什么？"},
    {"role": "assistant", "content": "Token 是模型处理文本时使用的基本单位。"},
]


def build_messages(user_input: Any) -> list[dict[str, str]]:
    """把用户输入转换成包含 system 和 user 的消息列表。"""
    if not isinstance(user_input, str):
        raise ValueError("user_input 必须是字符串")
    cleaned_input = user_input.strip()
    if not cleaned_input:
        raise ValueError("用户输入不能为空")
    
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": cleaned_input},
    ]
