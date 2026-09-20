from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from s01_l01_first_api.model import call_model


def make_client(response: object = None, error: Exception | None = None) -> Mock:
    client = Mock()
    if error:
        client.chat.completions.create.side_effect = error
    else:
        client.chat.completions.create.return_value = response
    return client


def test_normalizes_chat_completion_response() -> None:
    response = SimpleNamespace(
        id="req_demo",
        choices=[SimpleNamespace(message=SimpleNamespace(content="闭包会保留其词法作用域。"))],
        usage=SimpleNamespace(prompt_tokens=12, completion_tokens=8, total_tokens=20),
    )
    client = make_client(response)

    result = call_model("解释闭包", client=client, model="test-model")

    client.chat.completions.create.assert_called_once_with(
        model="test-model",
        messages=[{"role": "user", "content": "解释闭包"}],
    )
    assert result == {
        "text": "闭包会保留其词法作用域。",
        "request_id": "req_demo",
        "model": "test-model",
        "usage": {"input_tokens": 12, "output_tokens": 8, "total_tokens": 20},
    }


def test_uses_none_when_usage_is_missing() -> None:
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="ok"))]
    )
    result = call_model("hello", client=make_client(response), model="test-model")
    assert result["usage"] == {
        "input_tokens": None,
        "output_tokens": None,
        "total_tokens": None,
    }


@pytest.mark.parametrize(
    ("error", "message"),
    [
        (
            type("UnauthorizedError", (Exception,), {"status_code": 401})("unauthorized"),
            "密钥|认证|401",
        ),
        (type("APITimeoutError", (Exception,), {})("timed out"), "网络|代理|连接"),
        (
            type(
                "QuotaError",
                (Exception,),
                {
                    "status_code": 429,
                    "code": "credit_balance_exhausted",
                    "type": "insufficient_quota",
                },
            )("no credits"),
            "额度已用尽|充值",
        ),
    ],
)
def test_preserves_cause_and_returns_actionable_error(
    error: Exception, message: str
) -> None:
    with pytest.raises(RuntimeError, match=message) as raised:
        call_model("hello", client=make_client(error=error), model="test-model")
    assert raised.value.__cause__ is error
