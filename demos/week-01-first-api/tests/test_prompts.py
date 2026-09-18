import pytest

from week01_first_api.prompts import PROMPTS, get_prompt


def test_contains_four_comparable_prompts() -> None:
    assert list(PROMPTS) == ["direct", "audience", "example", "concise"]


def test_reads_named_prompt() -> None:
    assert get_prompt("direct") == "解释 Python 闭包。"


def test_rejects_unknown_prompt() -> None:
    with pytest.raises(ValueError, match="可选值"):
        get_prompt("unknown")

