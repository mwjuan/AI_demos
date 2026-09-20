from __future__ import annotations

import sys
from pathlib import Path


LESSON_DIR = Path(__file__).resolve().parent
FIRST_LESSON_SRC = LESSON_DIR.parents[0] / "s01-l01-first-api" / "src"
sys.path.insert(0, str(LESSON_DIR))
sys.path.insert(0, str(FIRST_LESSON_SRC))

from structured_output import parse_study_card  # noqa: E402
from s01_l01_first_api.client import create_model_client  # noqa: E402
from s01_l01_first_api.config import load_config  # noqa: E402
from s01_l01_first_api.runtime import load_lesson_environment  # noqa: E402


SYSTEM_PROMPT = (
    "只返回一个 JSON 对象，不要使用 Markdown 代码块，也不要添加解释。"
    "对象必须包含 term 和 definition，两个值都必须是字符串。"
)
USER_PROMPT = "为大语言模型中的 Token 生成学习卡片，definition 不超过 60 个汉字。"


def main() -> None:
    load_lesson_environment()
    config = load_config()
    client = create_model_client(config)

    try:
        response = client.chat.completions.create(
            model=config.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT},
            ],
        )
        raw_text = response.choices[0].message.content or ""
        print(f"模型原始输出：\n{raw_text}\n")
        card = parse_study_card(raw_text)
        print(f"校验后的 Python 字典：\n{card}")
    finally:
        client.close()


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        raise SystemExit(f"结构化输出校验失败：{error}") from error
