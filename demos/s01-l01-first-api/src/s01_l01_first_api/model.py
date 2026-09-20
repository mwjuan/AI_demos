from __future__ import annotations

from typing import Any


def call_model(prompt: str, *, client: Any, model: str) -> dict[str, Any]:
    """调用模型，并把供应商响应转换为课程统一使用的结果。"""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        usage = getattr(response, "usage", None)
        return {
            "text": response.choices[0].message.content,
            "request_id": getattr(response, "id", None),
            "model": model,
            "usage": {
                "input_tokens": getattr(usage, "prompt_tokens", None),
                "output_tokens": getattr(usage, "completion_tokens", None),
                "total_tokens": getattr(usage, "total_tokens", None),
            },
        }
    except Exception as error:
        status = getattr(error, "status_code", None) or getattr(error, "status", None)
        name = type(error).__name__
        message = str(error)
        is_connection_failure = name in {
            "APIConnectionError",
            "APITimeoutError",
            "APIConnectionTimeoutError",
        } or any(text in message.lower() for text in ("connection error", "timed out"))

        if is_connection_failure:
            friendly = "无法连接模型服务：请检查网络、代理设置和当前提供商的接口地址。"
        elif status == 401:
            friendly = "未授权：请检查当前提供商的 API 密钥是否正确。"
        elif status == 429:
            code = getattr(error, "code", None)
            error_type = getattr(error, "type", None)
            if code == "credit_balance_exhausted" or error_type == "insufficient_quota":
                friendly = (
                    "OpenAI API 额度已用尽：请在 OpenAI Platform 的 Billing 页面"
                    "充值或添加额度。"
                )
            else:
                friendly = "请求过多：请稍后再试，或检查您的使用配额。"
        elif isinstance(status, int) and status >= 500:
            friendly = "模型服务暂时不可用：请稍后再试。"
        else:
            friendly = f"调用模型失败：{message}"

        raise RuntimeError(friendly) from error

