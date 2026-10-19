from __future__ import annotations

from typing import Any

import httpx
from s01_l01_first_api.config import load_config
from s01_l01_first_api.client import create_model_client
from s01_l01_first_api.runtime import load_lesson_environment
from openai import APITimeoutError, APIConnectionError, APIStatusError

OLLAMA_CHAT_URL = "http://127.0.0.1:11434/api/chat"


class OllamaChatError(RuntimeError):
    """Ollama 没有返回可安全展示的完整回答。"""


def build_ollama_payload(
    model: Any,
    messages: Any,
) -> dict[str, Any]:
    """为 Ollama 创建包含完整聊天历史的请求体快照。"""
    # 1. model 必须是清理后非空的字符串。
    # 2. messages 必须是非空列表。
    # 3. 每条消息的 role 只能是 user 或 assistant。
    # 4. 每条 content 必须是清理后非空的字符串。
    # 5. 创建新的消息字典列表，不要直接复用 session_state 中的可变列表。
    # 6. 返回 model、messages、stream=False、think=False。

    if not isinstance(messages, list) or not messages:
        raise ValueError("messages must be a non-empty list.")
    if not isinstance(model, str) or not model.strip():
        raise ValueError("model must be a non-empty string.")

    cleaned_messages: list[dict[str, str]] = []

    for message in messages:
        if not isinstance(message, dict):
            raise ValueError("消息必须是字典")
        if "role" not in message or "content" not in message:
            raise ValueError("Each message must have 'role' and 'content' keys.")

        role = message.get("role")
        content = message.get("content")

        if role not in ["user", "assistant"]:
            raise ValueError("Each message's role must be 'user' or 'assistant'.")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Each message's content must be a non-empty string.")
        cleaned_messages.append({"role": role, "content": content.strip()})

    return {
        "model": model.strip(),
        "messages": cleaned_messages,
        "stream": False,
        "think": False,
    }


def extract_assistant_reply(data: Any) -> str:
    """从 Ollama 响应中提取可展示的完整助手回答。"""
    # 1. data 必须是字典。
    # 2. done_reason 必须等于 stop；否则错误中包含实际原因。
    # 3. message 必须是字典，其中 content 必须是清理后非空的字符串。
    # 4. 返回清理后的 content。
    if not isinstance(data, dict):
        raise OllamaChatError("Ollama 响应必须是字典")
    if "done_reason" not in data or "message" not in data:
        raise OllamaChatError("Ollama 响应必须包含 'done_reason' 和 'message' 键。")
    if not isinstance(data["message"], dict):
        raise OllamaChatError("Ollama 响应缺少有效的message.content")
    content = data["message"].get("content")
    reason = data.get("done_reason")
    if not isinstance(content, str) or not content.strip():
        raise OllamaChatError("Ollama 响应['message']['content'] 必须是清理后非空的字符串。")
    if reason is None:
        raise OllamaChatError("Ollama 响应['done_reason'] 不能为 None。")
    if reason != "stop":
        raise OllamaChatError(f"Ollama 响应['done_reason'] 必须是 'stop'，实际为 '{reason}'。")

    return content.strip()


def request_ollama_reply(
    model: Any,
    messages: Any,
    *,
    timeout: float = 120.0,
) -> str:
    """向本机 Ollama 发送完整聊天历史，并返回可展示的回答。"""
    # TODO 第六轮：
    # 1. 复用 build_ollama_payload() 构造请求体。
    # 2. 使用 httpx.Client(trust_env=False) 请求 OLLAMA_CHAT_URL。
    # 3. 先处理 HTTP/连接/超时/JSON 错误，再复用
    #    extract_assistant_reply() 验证并返回回答。
    payload = build_ollama_payload(model, messages)
    with httpx.Client(trust_env=False, timeout=timeout) as client:
        try:
            response = client.post(OLLAMA_CHAT_URL, json=payload,timeout=timeout)
            response.raise_for_status()
            data = response.json()
            return extract_assistant_reply(data)
        
        except httpx.TimeoutException as e:
            raise OllamaChatError(
                "请求 Ollama 超时，请稍后重试。"
            ) from e
        except httpx.ConnectError as e:
            raise OllamaChatError(
                "无法连接 Ollama，请确认服务已经启动。"
            ) from e
        except httpx.RequestError as e:
            raise OllamaChatError(
                f"请求 Ollama 时发生网络错误：{e}"
            ) from e
        except httpx.HTTPStatusError as e:
            detail = e.response.text
            try:
                error_data = e.response.json()
                if isinstance(error_data, dict):
                    detail = error_data.get("error") or detail
            except ValueError:
                pass

            raise OllamaChatError(
                f"Ollama HTTP {e.response.status_code}：{detail}"
            ) from e
        except ValueError as e:
            raise OllamaChatError(
                "Ollama 响应不是有效的 JSON，无法解析回答。"
            ) from e

def request_ollama_reply_practice(
    model: Any,
    messages: Any,
    *,
    timeout: float = 120.0,
) -> str:
    """向本机 Ollama 发送完整聊天历史，并返回可展示的回答流。"""
    payload = build_ollama_payload(model, messages)
    with httpx.Client(trust_env=False, timeout=timeout) as client:
        try:
            response = client.post(OLLAMA_CHAT_URL, json=payload, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            return extract_assistant_reply(data)
        except httpx.TimeoutException as e:
            raise OllamaChatError(
                "请求 Ollama 超时，请稍后重试。"
            ) from e
        except httpx.ConnectError as e:
            raise OllamaChatError(
                "无法连接 Ollama，请确认服务已经启动。"
            ) from e
        except httpx.RequestError as e:
            raise OllamaChatError(
                f"请求 Ollama 时发生网络错误：{e}"
            ) from e
        except httpx.HTTPStatusError as e:
            detail = e.response.text
            try:
                error_data = e.response.json()
                if isinstance(error_data, dict):
                    detail = error_data.get("error") or detail
            except ValueError:
                pass

            raise OllamaChatError(
                f"Ollama HTTP {e.response.status_code}：{detail}"
            ) from e
        except ValueError as e:
            raise OllamaChatError(
                "Ollama 响应不是有效的 JSON，无法解析回答。"
            ) from e
        
def request_reply(
    provider: str,
    model: str,
    messages: list[dict[str, str]], 
    *,
    timeout: float = 120.0,
) -> str:
    if provider == "ollama":
        return request_ollama_reply(model, messages, timeout=timeout)
    elif provider == "cloud":
        load_lesson_environment()
        config = load_config()

        with create_model_client(config) as client:
            return request_cloud_reply(
                model,
                messages,
                client=client,
                timeout=timeout,
            )
    else:
        raise ValueError(f"暂不支持模型来源：{provider}")
    

def extract_cloud_reply(response) -> str:
    # 1. choices 为空时，抛出 RuntimeError
    if not response.choices:
        raise RuntimeError("choices is empty")
    
    choice = response.choices[0]
    reason = choice.finish_reason
    content = choice.message.content
    
    # 2. finish_reason 不等于 "stop" 时，抛出 RuntimeError
    if reason != "stop":
        raise RuntimeError(f"finish_reason must be 'stop', got '{reason}'")
    # 3. content 不是字符串或去除空白后为空时，抛出 RuntimeError
    if not isinstance(content, str):
        raise RuntimeError(f"content must be a string, got {type(content)}")
    content = content.strip()
    if not content:
        raise RuntimeError("content is empty after stripping")
    # 4. 返回去除前后空白的 content
    return content


def request_cloud_reply(
    model: str,
    messages: list[dict[str, str]],
    *,
    client,
    timeout: float = 120.0,
) -> str:
    try:
        # ① 使用 client 发送完整历史，结果保存到 response
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            timeout=timeout,
        )

        # 记录服务目标与响应标识，供本课验证调用来源。
        print(
            f"[cloud] 收到响应：服务域名={client.base_url.host} "
            f"模型={response.model} 响应ID={response.id} "
            f"请求ID={getattr(response, '_request_id', None) or '未提供'}",
            flush=True,
        )
        
        # ② 调用 extract_cloud_reply(response)，并返回结果
        return extract_cloud_reply(response)
    except APITimeoutError as e:
        raise RuntimeError(f"请求云端模型超时") from e
    except APIConnectionError as e:
        raise RuntimeError(f"无法连接云端模型") from e
    except APIStatusError as e:
        raise RuntimeError(f"云端模型返回错误状态码 {e.status_code}") from e
    
