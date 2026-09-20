from __future__ import annotations

import argparse

from .client import create_model_client
from .config import load_config
from .model import call_model
from .prompts import get_prompt
from .runtime import load_lesson_environment


def main() -> None:
    parser = argparse.ArgumentParser(description="运行第一课的单次模型请求")
    parser.add_argument("prompt_name", nargs="?", default="direct")
    args = parser.parse_args()

    try:
        load_lesson_environment()
        config = load_config()
        prompt = get_prompt(args.prompt_name)
        client = create_model_client(config)
        try:
            print(f"\n提示词版本：{args.prompt_name}")
            print(f"提供商：{config.provider}")
            print(f"模型：{config.model}")
            print(f"代理：{'已启用' if config.proxy_url else '未启用'}")
            print(f"\n输入：\n{prompt}\n")

            result = call_model(prompt, client=client, model=config.model)
            print(f"回答：\n{result['text']}\n")
            print("用量：", result["usage"])
            print("请求 ID：", result["request_id"] or "服务未返回")
        finally:
            client.close()
    except (ValueError, RuntimeError) as error:
        parser.exit(1, f"\n运行失败：{error}\n")

