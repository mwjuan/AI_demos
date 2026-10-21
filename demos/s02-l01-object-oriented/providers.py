"""S02-L01 提供商练习：封装第一阶段已验证的模型请求函数。"""

import sys
from pathlib import Path

# 暂时复用第六课模块，沿用主线入口的导入方式；本课整合时再整理模块位置。
previous_lesson = Path(__file__).resolve().parents[1] / "s01-l06-streamlit-chat"
if str(previous_lesson) not in sys.path:
    sys.path.insert(0, str(previous_lesson))

from model_chat import request_ollama_reply, request_reply


class OllamaProvider:
    """使用配置对象中的本地模型和超时请求 Ollama。"""

    def __init__(self, config):
        # TODO 1：把传入的配置对象保存在当前实例的 config 属性上。
        self.config = config

    def reply(self, messages):
        # TODO 2：调用已导入的 request_ollama_reply，并返回回答。
        # 每次从 self.config 读取 local_model 和 timeout，传入完整 messages。
        # 原函数签名：request_ollama_reply(model, messages, *, timeout=120.0)
        return request_ollama_reply(
            model=self.config.local_model,
            messages=messages,
            timeout=self.config.timeout
        )


class CloudProvider:
    """复用统一入口，由旧模块负责云端配置和客户端的创建与关闭。"""

    def __init__(self, config):
        # TODO 3：保存传入的配置对象，方式与本地提供商相同。
        self.config = config

    def reply(self, messages):
        # TODO 4：复用 request_reply，固定 provider="cloud"。
        # 使用当前配置的 cloud_model、timeout，转交完整 messages 并返回回答。
        # 原函数签名：request_reply(provider, model, messages, *, timeout=120.0)
        return request_reply(
            provider="cloud",
            model=self.config.cloud_model,
            messages=messages,
            timeout=self.config.timeout
        )


def create_provider(config):
    """按当前配置选择提供商对象，不在选择时发送请求。"""
    # TODO 5：ollama 返回 OllamaProvider 实例，cloud 返回 CloudProvider 实例。
    # 将传入的 config 交给选中的类；其他来源抛出 ValueError。
    if config.provider == "ollama":
        return OllamaProvider(config)
    elif config.provider == "cloud":
        return CloudProvider(config)
    else:
        raise ValueError(f"未知提供商：{config.provider}")
        # 也可以直接使用 NotImplementedError，但 ValueError 更贴切。
        #  raise NotImplementedError("请实现提供商选择")
