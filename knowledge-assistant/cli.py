"""S01 主线练习：复用统一模型入口，完成一次命令行问答。"""

from __future__ import annotations

import sys
from pathlib import Path


# 直接引用第六课的调用逻辑，不复制已完成的函数。
lesson_dir = Path(__file__).resolve().parents[1] / "demos" / "s01-l06-streamlit-chat"
sys.path.insert(0, str(lesson_dir))

from model_chat import request_reply


def main() -> None:
    provider = "ollama"
    model = "qwen3:4b"
    timeout = 120.0

    # TODO 1：使用 input() 读取问题，保存到 prompt。
    input_prompt = input("请输入您的问题：")
    # TODO 2：构造 messages，包含一条 role 为 user、content 为 prompt 的消息。
    messages = [{"role": "user", "content": input_prompt}]
    # TODO 3：调用 request_reply，传递上面的来源、模型、历史和超时。
    # TODO 4：用 try / except / else 处理失败和成功，分别打印错误或回答。
    try:
        reply = request_reply(provider, model, messages, timeout=timeout)
    except RuntimeError as e:
        print(f"错误：{e}") 
    except ValueError as e:
        print(f"错误：{e}") 
    else:
        print(f"回答：{reply}")
        messages.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    main()
