# S01-L02：Python 数据、控制流与容器

昨天你已经能调用阿里云百炼。今天先不发起新的网络请求，而是处理模型应用里最常见的一种数据：对话消息列表。

```python
messages = [
    {"role": "user", "content": "解释一下 Token"},
    {"role": "assistant", "content": "Token 是模型处理文本的基本单位。"},
]
```

这段数据从外到内有三层：

1. `messages` 是变量，保存一个列表 `list`。
2. 列表中的每条消息是字典 `dict`。
3. `role` 和 `content` 对应的值是字符串 `str`。

如果你熟悉 JavaScript，可以先这样类比：

| JavaScript | Python | 本课用途 |
|---|---|---|
| `const messages = []` | `messages = []` | 保存消息列表 |
| `{ role: "user" }` | `{"role": "user"}` | 表示一条消息 |
| `value.trim()` | `value.strip()` | 清除首尾空白 |
| `typeof value === "string"` | `isinstance(value, str)` | 检查数据类型 |
| `for (const item of items)` | `for item in items` | 逐条处理消息 |
| `if (...) {}` | `if ...:` | 根据条件选择分支 |
| `throw new Error(...)` | `raise ValueError(...)` | 拒绝异常输入 |

## 今天的目标

完成 `conversation_stats.py` 中的两个函数：

- `normalize_message(message)`：验证并清洗一条消息。
- `summarize_messages(messages)`：循环处理多条消息并生成统计结果。

输入中的空白消息不计入统计；结构或类型错误必须明确报错，不能悄悄吞掉。

正常返回结果的结构是：

```python
{
    "message_count": 3,
    "role_counts": {"user": 2, "assistant": 1},
    "total_chars": 26,
    "longest_message": "最长的那条消息",
}
```

## 第一轮：先读数据，不急着写

打开 `conversation_stats.py`，从 `SAMPLE_MESSAGES` 开始，回答：

1. 外层列表中有几项？4项
2. 哪一项会因为清理后为空而被忽略？content为空字符串会因为strip后为空而被忽略
3. `role_counts[role] += 1` 为什么可以同时统计两个角色？因为role_counts是字典，使用role作为不同的key
4. 如果 `content` 是数字，为什么不应该自动转成字符串？因为表示输入的类型不正确

## 第二轮：实现 `normalize_message`

按这个顺序写判断：

1. `message` 必须是字典，否则抛出 `ValueError`。
2. `role` 必须是 `user` 或 `assistant`。
3. `content` 必须是字符串。
4. 用 `strip()` 清理内容；清理后为空则返回 `None`。
5. 否则返回一个新的、清理过的消息字典。

只做完这一部分时运行：

```bash
pytest demos/s01-l02-python-data/tests/test_conversation_stats.py -k normalize
```

## 第三轮：实现 `summarize_messages`

准备四个变量，再用一次 `for` 循环完成统计：

- `message_count`
- `role_counts`
- `total_chars`
- `longest_message`

每次循环先调用 `normalize_message`。遇到 `None` 就用 `continue` 跳过；否则更新四项统计。

完成后运行：

```bash
pytest demos/s01-l02-python-data/tests/test_conversation_stats.py
python demos/s01-l02-python-data/conversation_stats.py
```

## 独立变式挑战

测试全部通过后，自己增加 `average_chars`：有效消息的平均字符数，保留一位小数；没有有效消息时返回 `0.0`。先写下预期，再改代码和测试。

## 完成标准

- 自动测试全部通过。
- 能解释列表、字典、字符串在数据中的位置。
- 能解释 `if`、`for`、`continue` 各自控制了什么。
- 完成独立变式挑战。
- 填写 `reflection.md`。

