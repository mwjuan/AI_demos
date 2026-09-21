from __future__ import annotations

from typing import Any

import httpx


OLLAMA_CHAT_URL = "http://127.0.0.1:11434/api/chat"


class OllamaRequestError(RuntimeError):
    """无法从本机 Ollama 获得有效响应。"""


def build_chat_payload(model: Any, prompt: Any) -> dict[str, Any]:
    """构造发送给 Ollama /api/chat 的 JSON 请求体。"""
    # 完成类型检查、空白清理、空值检查和请求体构造。
    if model is None or not isinstance(model, str):
        raise ValueError("model必须是字符串")
    
    if prompt is None or not isinstance(prompt, str):
        raise ValueError("prompt必须是字符串")
    
    if not model.strip():
        raise ValueError("model不能为空字符串")
    if not prompt.strip():
        raise ValueError("prompt不能为空字符串")
    
    cleaned_model = model.strip()
    cleaned_prompt = prompt.strip()
    
    if not cleaned_model:
        raise ValueError("model不能为空字符串")
    if not cleaned_prompt:
        raise ValueError("prompt不能为空字符串")
    
    return {
        "model": cleaned_model,
        "messages": [
            {"role": "user", "content": cleaned_prompt}
        ],
        "stream": False,
        "think": False,
    }


def request_chat(
    model: Any,
    prompt: Any,
    *,
    timeout: float = 60.0,
) -> dict[str, Any]:
    """向本机 Ollama 发送一次非流式聊天请求并返回 JSON 对象。"""
    # 构造请求体，调用 httpx.post，并处理连接、超时和 HTTP 错误。
    payload = build_chat_payload(model, prompt)  # 验证并构建请求体
    try:
        response = httpx.post(OLLAMA_CHAT_URL, json=payload, timeout=timeout)  # 发送请求
        response.raise_for_status()  # 检查 HTTP 错误
        result = response.json()  # 解析 JSON 响应
        if not isinstance(result, dict):
            raise OllamaRequestError("Ollama 响应不是有效的 JSON 对象")
        return result
    except httpx.HTTPStatusError as e:
        raise OllamaRequestError(f"请求 Ollama 时发生错误: {e}") from e
    except httpx.TimeoutException as e:
        raise OllamaRequestError(f"请求 Ollama 超时: {e}") from e
    except httpx.ConnectError as e:
        raise OllamaRequestError(f"无法连接到 Ollama: {e}") from e
    except Exception as e:
        raise OllamaRequestError(f"未预期的错误: {e}") from e


def summarize_chat_response(data: Any) -> dict[str, Any]:
    """从 Ollama 原始响应中提取回答和便于比较的性能指标。"""
    # 验证响应结构，把纳秒换算成秒，并计算每秒生成 token 数。
    if not isinstance(data, dict):
        raise OllamaRequestError("响应缺少有效的 message.content")

    message = data.get("message")
    if not isinstance(message, dict):
        raise OllamaRequestError("响应缺少有效的 message.content")

    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise OllamaRequestError("响应缺少有效的 message.content")
    
    total_duration = data.get("total_duration", 0)
    load_duration = data.get("load_duration", 0)
    eval_duration = data.get("eval_duration", 0)
    output_tokens = data.get("eval_count", 0)
    prompt_tokens = data.get("prompt_eval_count", 0)
    
    total_seconds = total_duration / 1_000_000_000
    load_seconds = load_duration / 1_000_000_000
    
    if eval_duration <= 0:
        tokens_per_second = 0.0
    else:
        tokens_per_second = output_tokens / (eval_duration / 1_000_000_000)
    
    return {
        "model": data.get("model"),
        "content": content.strip(),
        "done_reason": data.get("done_reason"),
        "total_seconds": total_seconds,
        "load_seconds": load_seconds,
        "prompt_tokens": prompt_tokens,
        "output_tokens": output_tokens,
        "tokens_per_second": tokens_per_second,
    }


def require_complete_response(data: Any) -> dict[str, Any]:
    """返回完整响应的摘要；生成未正常结束时抛出清晰错误。"""
    # 1. 调用 summarize_chat_response(data)，不要重复解析响应。
    # 2. 检查摘要中的 done_reason 是否等于 "stop"。
    # 3. 不等于 "stop" 时抛出 OllamaRequestError，消息中包含实际结束原因。
    # 4. 正常结束时返回摘要。
    response = summarize_chat_response(data)
    reason = response["done_reason"]

    if reason is None:
        raise OllamaRequestError("响应缺少 done_reason 字段")
    if reason != "stop":
        raise OllamaRequestError(f"生成未正常结束，结束原因: {reason}")
    return response
