from __future__ import annotations

import sys
from pathlib import Path


FIRST_LESSON_SRC = (
    Path(__file__).resolve().parents[1]
    / "s01-l01-first-api"
    / "src"
)
sys.path.insert(0, str(FIRST_LESSON_SRC))

from s01_l01_first_api.client import create_model_client  # noqa: E402
from s01_l01_first_api.config import load_config  # noqa: E402
from s01_l01_first_api.runtime import load_lesson_environment  # noqa: E402


USER_QUESTION = "解释大语言模型处理文本时的 Token，不要讨论登录认证 Token。"
SYSTEM_PROMPTS = {
    "concise": "使用简洁的中文回答，不超过 80 个汉字。",
    "analogy": "使用生活化比喻，向小学生解释；不超过 80 个汉字。",
}


def main() -> None:
    load_lesson_environment()
    config = load_config()
    client = create_model_client(config)

    try:
        for name, system_prompt in SYSTEM_PROMPTS.items():
            response = client.chat.completions.create(
                model=config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": USER_QUESTION},
                ],
            )
            answer = response.choices[0].message.content
            print(f"\n=== {name} ===")
            print(f"system: {system_prompt}")
            print(f"user: {USER_QUESTION}")
            print(f"assistant: {answer}")
    finally:
        client.close()


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError) as error:
        raise SystemExit(f"实验失败：{error}") from error
