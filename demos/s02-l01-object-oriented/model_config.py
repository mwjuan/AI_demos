"""S02-L01 练习骨架：先完成初始化，再实现恢复方法。"""


class ModelConfig:
    """一个聊天配置实例，负责设置数据，不负责界面或模型请求。"""

    def __init__(self):
        # TODO 1：在当前实例上保存来源、两个模型名和超时的默认值。
        self.provider = "ollama"
        self.local_model = "qwen3:4b"
        self.cloud_model = "qwen-plus"
        self.timeout = 120.0
        # 属性名称与预期值见本课 README 的第一轮。

    def reset(self):
        self.provider = "ollama"
        self.local_model = "qwen3:4b"
        self.cloud_model = "qwen-plus"
        self.timeout = 120.0
