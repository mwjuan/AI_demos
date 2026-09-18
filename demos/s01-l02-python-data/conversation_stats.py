from __future__ import annotations

from typing import Any


SAMPLE_MESSAGES = [
    {"role": "user", "content": "  什么是大模型的上下文？  "},
    {"role": "assistant", "content": "上下文是模型本次回答时能够参考的信息。"},
    {"role": "user", "content": "   "},
    {"role": "user", "content": "上下文越长越好吗？"},
]


def normalize_message(message: Any) -> dict[str, str] | None:
    """验证并清洗一条消息；空消息返回 None。"""
    # TODO 1：检查 message、role 和 content 的类型与取值。
    if not isinstance(message, dict):
        raise ValueError("message 必须是字典")

    if "role" not in message or "content" not in message:
        raise ValueError("消息必须包含 role 和 content")
    
    role = message.get("role")
    content = message.get("content")

    if role not in ["user", "assistant"]:
        raise ValueError("role 必须是 'user' 或 'assistant'")
    if not isinstance(content, str):
        raise ValueError("content 必须是字符串")
    
    # TODO 2：清除 content 首尾空白，空内容返回 None。
    content = content.strip()
    if not content:
        return None
    # TODO 3：返回只包含 role 和清洗后 content 的新字典。
    return {"role": role, "content": content}

def summarize_messages(messages: list[Any]) -> dict[str, Any]:
    """统计有效对话消息；异常输入由 normalize_message 明确拒绝。"""
    message_count = 0
    role_counts = {"user": 0, "assistant": 0}
    total_chars = 0
    longest_message = ""
    average_chars = 0.0

    # TODO 4：使用 for 循环逐条调用 normalize_message。
    for message in messages:
        normalized = normalize_message(message)
         # TODO 5：跳过空消息，更新上面的四个变量。
        if normalized is None:
            continue
        message_count += 1
        role_counts[normalized['role']] += 1
        total_chars += len(normalized['content'])
        if len(normalized['content']) > len(longest_message):
            longest_message = normalized['content']
    if message_count > 0:
        average_chars = round(total_chars / message_count, 1)
    return {
        "message_count": message_count,
        "role_counts": role_counts,
        "total_chars": total_chars,
        "longest_message": longest_message,
        "average_chars": average_chars
    }

def main() -> None:
    summary = summarize_messages(SAMPLE_MESSAGES)
    print("对话统计结果")
    print(f"有效消息：{summary['message_count']}")
    print(f"角色数量：{summary['role_counts']}")
    print(f"总字符数：{summary['total_chars']}")
    print(f"最长消息：{summary['longest_message']}")
    print(f"平均字符数：{summary['average_chars']:.1f}")


if __name__ == "__main__":
    main()

