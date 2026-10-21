"""S01 主线练习：复用统一模型入口，完成一次命令行问答。"""

from __future__ import annotations

import sys
from pathlib import Path


# 直接引用第六课的调用逻辑，不复制已完成的函数。
lesson_dir = Path(__file__).resolve().parents[1] / "demos" / "s01-l06-streamlit-chat"
sys.path.insert(0, str(lesson_dir))

from model_chat import request_reply

# S02-L01：先接入已完成的类，main() 中的调用流程由学习者重构。
object_lesson_dir = Path(__file__).resolve().parents[1] / "demos" / "s02-l01-object-oriented"
sys.path.insert(0, str(object_lesson_dir))

from model_config import ModelConfig
from chat_session import ChatSession
from providers import create_provider


def main() -> None:
    # S02-L01 TODO：用配置和会话实例替换分散的设置与消息列表；
    # 在 try 中校验并追加用户消息、选择提供商、传入快照获取回答。
    # 保留两种错误提示；成功时通过会话方法追加助手消息并打印回答。
    model_config = ModelConfig()
    chat_session = ChatSession()
    try:
        # TODO 1：使用 input() 读取问题，保存到 prompt。
        prompt = input("请输入您的问题：")
        # TODO 2：调用会话实例的 append_message()，传入 role="user" 和 content=prompt。
        chat_session.append_message(role="user", content=prompt)
        # TODO 3：调用配置实例的属性，获取来源、模型名和超时。
        provider = create_provider(model_config)
        model = model_config.local_model
        timeout = model_config.timeout
        # TODO 4：调用会话实例的 snapshot()，获取消息快照。
        messages_snapshot = chat_session.snapshot()
        # TODO 5：调用 request_reply()，传入来源、模型名、消息快照和超时。
        reply = provider.reply(messages_snapshot)
    except RuntimeError as e:
        print(f"错误：{e}")
    except ValueError as e:
        print(f"错误：{e}")
    else:
        # TODO 6：调用会话实例的 append_message()，传入 role="assistant" 和 content=reply。
        chat_session.append_message(role="assistant", content=reply)
        print(f"回答：{reply}")
        
        
    # provider = "ollama"
    # model = "qwen3:4b"
    # timeout = 120.0

    # # TODO 1：使用 input() 读取问题，保存到 prompt。
    # input_prompt = input("请输入您的问题：")
    # # TODO 2：构造 messages，包含一条 role 为 user、content 为 prompt 的消息。
    # messages = [{"role": "user", "content": input_prompt}]
    # # TODO 3：调用 request_reply，传递上面的来源、模型、历史和超时。
    # # TODO 4：用 try / except / else 处理失败和成功，分别打印错误或回答。
    # try:
    #     reply = request_reply(provider, model, messages, timeout=timeout)
    # except RuntimeError as e:
    #     print(f"错误：{e}") 
    # except ValueError as e:
    #     print(f"错误：{e}") 
    # else:
    #     print(f"回答：{reply}")
    #     messages.append({"role": "assistant", "content": reply})

if __name__ == "__main__":
    main()
