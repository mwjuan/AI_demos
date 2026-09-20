from __future__ import annotations

import sys
from pathlib import Path

import pytest


LESSON_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LESSON_DIR))

from structured_output import parse_json_object, parse_study_card  # noqa: E402


def test_parse_json_object_returns_dictionary() -> None:
    assert parse_json_object('{"term": "Token"}') == {"term": "Token"}


def test_parse_json_object_rejects_broken_json() -> None:
    with pytest.raises(ValueError, match="JSON"):
        parse_json_object('{"term": "Token"')


def test_parse_json_object_rejects_json_array() -> None:
    with pytest.raises(ValueError, match="对象"):
        parse_json_object('["Token"]')


def test_parse_json_object_rejects_non_string_input() -> None:
    with pytest.raises(ValueError, match="字符串"):
        parse_json_object({"term": "Token"})


def test_parse_study_card_returns_clean_fields() -> None:
    assert parse_study_card(
        '{"term": "  Token  ", "definition": "  模型处理文本的基本单位  "}'
    ) == {
        "term": "Token",
        "definition": "模型处理文本的基本单位",
    }


@pytest.mark.parametrize(
    "text",
    [
        '{"definition": "解释"}',
        '{"term": "Token"}',
        '{"term": 123, "definition": "解释"}',
        '{"term": "Token", "definition": "   "}',
    ],
)
def test_parse_study_card_rejects_invalid_fields(text: str) -> None:
    with pytest.raises(ValueError, match="term|definition"):
        parse_study_card(text)
