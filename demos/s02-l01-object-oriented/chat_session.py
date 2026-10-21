"""S02-L01 会话练习：每个实例分别管理自己的消息。"""


class ChatSession:
    """保存聊天历史，不负责界面、文件存取或模型请求。"""

    def __init__(self):
        # TODO 1：为当前实例创建独立的空消息列表，属性名为 messages。
        self.messages = []
        

    def clear(self):
        # TODO 2：下一步再做，只清空当前会话的消息。
        self.messages = []

    def append_message(self, role, content):
        # TODO 3：沿用第一阶段的消息规则，先验证、清理，再追加并返回消息。
        # 非法输入抛出 ValueError，且不能改变已有历史。详见本课 README。
        if role not in ["user", "assistant"]:
            raise ValueError("角色必须是 'user' 或 'assistant'")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("内容必须是非空字符串")
        message = {"role": role, "content": content.strip()}
        self.messages.append(message)
        return message

    def snapshot(self):
        # TODO 4：返回消息快照：列表和其中每个消息字典都与内部历史独立。
        # 消息只包含 role、content 两个字符串字段，详见本课 README。
        return [message.copy() for message in self.messages]
