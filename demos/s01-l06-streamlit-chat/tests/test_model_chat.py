from __future__ import annotations

import sys
from pathlib import Path

import httpx
import pytest


LESSON_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LESSON_DIR))

import model_chat  # noqa: E402
from model_chat import (  # noqa: E402
    OLLAMA_CHAT_URL,
    OllamaChatError,
    build_ollama_payload,
    extract_assistant_reply,
    request_ollama_reply,
)


def test_build_ollama_payload_contains_complete_history() -> None:
    messages = [
        {"role": "user", "content": "什么是 Token？"},
        {"role": "assistant", "content": "Token 是模型处理文本的单位。"},
        {"role": "user", "content": "再举一个例子。"},
    ]

    payload = build_ollama_payload("  qwen3:4b  ", messages)

    assert payload == {
        "model": "qwen3:4b",
        "messages": messages,
        "stream": False,
        "think": False,
    }


def test_build_ollama_payload_creates_message_snapshot() -> None:
    messages = [{"role": "user", "content": "解释 Token"}]

    payload = build_ollama_payload("qwen3:4b", messages)
    messages[0]["content"] = "后来被修改"
    messages.append({"role": "user", "content": "后来追加"})

    assert payload["messages"] == [
        {"role": "user", "content": "解释 Token"},
    ]


@pytest.mark.parametrize("model", [None, 123, "", "   "])
def test_build_ollama_payload_rejects_invalid_model(model: object) -> None:
    with pytest.raises(ValueError, match="model"):
        build_ollama_payload(model, [{"role": "user", "content": "你好"}])


@pytest.mark.parametrize("messages", [None, {}, [], "你好"])
def test_build_ollama_payload_rejects_invalid_messages(messages: object) -> None:
    with pytest.raises(ValueError, match="messages"):
        build_ollama_payload("qwen3:4b", messages)


@pytest.mark.parametrize(
    "message",
    [
        None,
        {},
        {"role": "system", "content": "帮助用户"},
        {"role": "user", "content": None},
        {"role": "assistant", "content": "   "},
    ],
)
def test_build_ollama_payload_rejects_invalid_message(message: object) -> None:
    with pytest.raises(ValueError, match="role|content|消息"):
        build_ollama_payload("qwen3:4b", [message])


def test_extract_assistant_reply_returns_clean_content() -> None:
    data = {
        "done_reason": "stop",
        "message": {"role": "assistant", "content": "  你好，有什么可以帮你？  "},
    }

    assert extract_assistant_reply(data) == "你好，有什么可以帮你？"


@pytest.mark.parametrize("data", [None, [], "unexpected"])
def test_extract_assistant_reply_rejects_non_object(data: object) -> None:
    with pytest.raises(OllamaChatError, match="响应"):
        extract_assistant_reply(data)


@pytest.mark.parametrize("reason", [None, "length", "load"])
def test_extract_assistant_reply_rejects_incomplete_output(reason: object) -> None:
    data = {
        "done_reason": reason,
        "message": {"role": "assistant", "content": "部分回答"},
    }

    expected = "done_reason" if reason is None else str(reason)
    with pytest.raises(OllamaChatError, match=expected):
        extract_assistant_reply(data)


@pytest.mark.parametrize(
    "message",
    [
        None,
        {},
        {"content": None},
        {"content": "   "},
    ],
)
def test_extract_assistant_reply_rejects_missing_content(message: object) -> None:
    data = {"done_reason": "stop", "message": message}

    with pytest.raises(OllamaChatError, match="content"):
        extract_assistant_reply(data)


def test_request_ollama_reply_posts_history_and_returns_answer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    messages = [{"role": "user", "content": "什么是 Token？"}]
    captured: dict[str, object] = {}

    def fake_post(
        client: httpx.Client,
        url: str,
        **kwargs: object,
    ) -> httpx.Response:
        captured["url"] = url
        captured.update(kwargs)
        return httpx.Response(
            200,
            json={
                "done_reason": "stop",
                "message": {
                    "role": "assistant",
                    "content": "Token 是模型处理文本的单位。",
                },
            },
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(model_chat.httpx.Client, "post", fake_post)

    reply = request_ollama_reply("qwen3:4b", messages, timeout=15.0)

    assert captured == {
        "url": OLLAMA_CHAT_URL,
        "json": build_ollama_payload("qwen3:4b", messages),
        "timeout": 15.0,
    }
    assert reply == "Token 是模型处理文本的单位。"


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (httpx.ConnectError("boom"), "无法连接"),
        (httpx.ReadTimeout("slow"), "超时"),
    ],
)
def test_request_ollama_reply_translates_network_errors(
    monkeypatch: pytest.MonkeyPatch,
    error: httpx.RequestError,
    expected: str,
) -> None:
    def fake_post(
        client: httpx.Client,
        url: str,
        **kwargs: object,
    ) -> httpx.Response:
        raise error

    monkeypatch.setattr(model_chat.httpx.Client, "post", fake_post)

    with pytest.raises(OllamaChatError, match=expected):
        request_ollama_reply(
            "qwen3:4b",
            [{"role": "user", "content": "什么是 Token？"}],
        )


def test_request_ollama_reply_includes_ollama_http_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_post(
        client: httpx.Client,
        url: str,
        **kwargs: object,
    ) -> httpx.Response:
        return httpx.Response(
            404,
            json={"error": "model 'missing' not found"},
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(model_chat.httpx.Client, "post", fake_post)

    with pytest.raises(OllamaChatError, match="404.*model 'missing' not found"):
        request_ollama_reply(
            "missing",
            [{"role": "user", "content": "什么是 Token？"}],
        )


def test_request_ollama_reply_rejects_invalid_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_post(
        client: httpx.Client,
        url: str,
        **kwargs: object,
    ) -> httpx.Response:
        return httpx.Response(
            200,
            text="not json",
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(model_chat.httpx.Client, "post", fake_post)

    with pytest.raises(OllamaChatError, match="JSON"):
        request_ollama_reply(
            "qwen3:4b",
            [{"role": "user", "content": "什么是 Token？"}],
        )
