from __future__ import annotations

import json
from typing import Any


SAMPLE_OUTPUT = '{"term": "Token", "definition": "模型处理文本的基本单位"}'


def parse_json_object(text: Any) -> dict[str, Any]:
    """把模型返回的 JSON 文本解析为 Python 字典。"""
    if not isinstance(text, str):
        raise ValueError("模型输出必须是字符串")
    
    try:
        data = json.loads(text)  # 解析 JSON 文本为 Python 字典
        if not isinstance(data, dict):
            raise ValueError("JSON 顶层必须是对象")
        return data
    except json.JSONDecodeError:
        raise ValueError("模型输出不是有效的 JSON 格式")


def parse_study_card(text: Any) -> dict[str, str]:
    """解析并验证包含 term 和 definition 的学习卡片。"""
    data = parse_json_object(text)  # 验证 JSON 格式
    term = data.get("term")
    definition = data.get("definition")
    
    if "term" not in data or "definition" not in data:
        raise ValueError("学习卡片必须包含 term 和 definition 字段")
    
    if not isinstance(term, str) or not isinstance(definition, str):
        raise ValueError("term 和 definition 字段必须是字符串")
    if not term.strip() or not definition.strip():
        raise ValueError("term 和 definition 字段不能为空")
    
    return {
        "term": term.strip(),  # 去除 term 字段的前后空白
        "definition": definition.strip(),  # 去除 definition 字段的前后空白
    }
