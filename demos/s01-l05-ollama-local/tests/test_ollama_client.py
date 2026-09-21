from __future__ import annotations

import sys
from pathlib import Path

import httpx
import pytest


LESSON_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LESSON_DIR))

import ollama_client  # noqa: E402
from ollama_client import (  # noqa: E402
    OLLAMA_CHAT_URL,
    OllamaRequestError,
    build_chat_payload,
    require_complete_response,
    request_chat,
    summarize_chat_response,
)


def test_build_chat_payload_returns_ollama_chat_shape() -> None:
    assert build_chat_payload("qwen3:4b", "解释 Token") == {
        "model": "qwen3:4b",
        "messages": [{"role": "user", "content": "解释 Token"}],
        "stream": False,
        "think": False,
    }


def test_build_chat_payload_strips_model_and_prompt() -> None:
    payload = build_chat_payload("  qwen3:4b  ", "  解释 Token  ")

    assert payload["model"] == "qwen3:4b"
    assert payload["messages"][0]["content"] == "解释 Token"


@pytest.mark.parametrize(
    ("model", "prompt"),
    [
        (None, "解释 Token"),
        (123, "解释 Token"),
        ("qwen3:4b", None),
        ("qwen3:4b", ["解释 Token"]),
    ],
)
def test_build_chat_payload_rejects_non_string_values(
    model: object, prompt: object
) -> None:
    with pytest.raises(ValueError, match="字符串"):
        build_chat_payload(model, prompt)


@pytest.mark.parametrize(
    ("model", "prompt"),
    [
        ("", "解释 Token"),
        ("   ", "解释 Token"),
        ("qwen3:4b", ""),
        ("qwen3:4b", "   "),
    ],
)
def test_build_chat_payload_rejects_blank_values(model: str, prompt: str) -> None:
    with pytest.raises(ValueError, match="不能为空"):
        build_chat_payload(model, prompt)


def test_request_chat_posts_payload_and_returns_json(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_post(url: str, **kwargs: object) -> httpx.Response:
        captured["url"] = url
        captured.update(kwargs)
        return httpx.Response(
            200,
            json={"message": {"role": "assistant", "content": "Token 是文本单位。"}},
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(ollama_client.httpx, "post", fake_post)

    result = request_chat("qwen3:4b", "解释 Token", timeout=12.0)

    assert captured == {
        "url": OLLAMA_CHAT_URL,
        "json": build_chat_payload("qwen3:4b", "解释 Token"),
        "timeout": 12.0,
    }
    assert result["message"]["content"] == "Token 是文本单位。"


@pytest.mark.parametrize(
    ("error", "message"),
    [
        (httpx.ConnectError("boom"), "无法连接"),
        (httpx.ReadTimeout("slow"), "超时"),
    ],
)
def test_request_chat_translates_network_errors(
    monkeypatch: pytest.MonkeyPatch,
    error: httpx.RequestError,
    message: str,
) -> None:
    def fake_post(url: str, **kwargs: object) -> httpx.Response:
        raise error

    monkeypatch.setattr(ollama_client.httpx, "post", fake_post)

    with pytest.raises(OllamaRequestError, match=message):
        request_chat("qwen3:4b", "解释 Token")


def test_request_chat_translates_http_status_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_post(url: str, **kwargs: object) -> httpx.Response:
        return httpx.Response(
            404,
            json={"error": "model not found"},
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(ollama_client.httpx, "post", fake_post)

    with pytest.raises(OllamaRequestError, match="404"):
        request_chat("missing-model", "解释 Token")


def test_request_chat_rejects_non_object_json(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_post(url: str, **kwargs: object) -> httpx.Response:
        return httpx.Response(
            200,
            json=["unexpected"],
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(ollama_client.httpx, "post", fake_post)

    with pytest.raises(OllamaRequestError, match="JSON 对象"):
        request_chat("qwen3:4b", "解释 Token")


SAMPLE_RESPONSE = {
    "model": "qwen3:4b",
    "message": {
        "role": "assistant",
        "content": "Token 是模型处理文本的基本单位。",
    },
    "done": True,
    "done_reason": "stop",
    "total_duration": 4_789_262_667,
    "load_duration": 1_044_081_250,
    "prompt_eval_count": 31,
    "eval_count": 80,
    "eval_duration": 3_576_289_000,
}


def test_summarize_chat_response_extracts_text_and_metrics() -> None:
    result = summarize_chat_response(SAMPLE_RESPONSE)

    assert result["model"] == "qwen3:4b"
    assert result["content"] == "Token 是模型处理文本的基本单位。"
    assert result["done_reason"] == "stop"
    assert result["total_seconds"] == pytest.approx(4.789262667)
    assert result["load_seconds"] == pytest.approx(1.04408125)
    assert result["prompt_tokens"] == 31
    assert result["output_tokens"] == 80
    assert result["tokens_per_second"] == pytest.approx(
        80 / 3.576289,
    )


@pytest.mark.parametrize(
    "data",
    [
        None,
        [],
        {},
        {"message": None},
        {"message": {}},
        {"message": {"content": "   "}},
    ],
)
def test_summarize_chat_response_rejects_missing_content(data: object) -> None:
    with pytest.raises(OllamaRequestError, match="content"):
        summarize_chat_response(data)


def test_summarize_chat_response_handles_zero_generation_duration() -> None:
    data = dict(SAMPLE_RESPONSE)
    data["eval_duration"] = 0

    result = summarize_chat_response(data)

    assert result["tokens_per_second"] == 0.0


def test_require_complete_response_returns_summary_for_stop() -> None:
    result = require_complete_response(SAMPLE_RESPONSE)

    assert result == summarize_chat_response(SAMPLE_RESPONSE)


def test_require_complete_response_rejects_truncated_output() -> None:
    data = dict(SAMPLE_RESPONSE)
    data["done_reason"] = "length"

    with pytest.raises(OllamaRequestError, match="length"):
        require_complete_response(data)


def test_require_complete_response_rejects_missing_done_reason() -> None:
    data = dict(SAMPLE_RESPONSE)
    data.pop("done_reason")

    with pytest.raises(OllamaRequestError, match="done_reason"):
        require_complete_response(data)
