# S01-L03：函数、模块、文件与异常

上一课的对话数据只存在内存里，程序退出后就消失了。今天把它保存到本地 JSON 文件，再从文件恢复。

这条数据流是：

```text
消息列表 → save_messages → JSON 文件 → load_messages → 消息列表
```

## 今天的目标

- 用函数把“保存”和“读取”拆成两个明确步骤。
- 从另一个模块导入上一课已经学过的消息清洗逻辑。
- 使用 `Path`、`open`、`json.dump` 和 `json.load` 读写 UTF-8 文件。
- 区分可恢复错误和损坏数据：文件不存在时返回空列表，JSON 损坏时明确报错。

## 先认识两个模块

- `message_utils.py`：只负责验证、清洗消息，不接触文件。
- `conversation_store.py`：只负责保存、读取，复用前一个模块。

这种拆分让每个函数只有一个主要职责。以后更换存储方式时，消息规则不需要跟着重写。

## 第一轮：完成 `save_messages`

打开 `conversation_store.py`，先只处理 `TODO 1` 到 `TODO 3`：

1. 用列表推导式逐条调用 `normalize_message`。
2. 清洗结果为 `None` 的空消息不写入文件。
3. 创建父目录，并以 UTF-8 写入 JSON；设置 `ensure_ascii=False`，让文件中的中文可直接阅读。

然后运行：

```bash
.venv/bin/python -m pytest demos/s01-l03-files-errors/tests/test_conversation_store.py -k save -q
```

第一次看到失败是正常的。先关注第一个失败，不要一次修改所有内容。

## 第二轮：完成 `load_messages`

1. 文件不存在时返回 `[]`，这是首次运行时的正常情况。
2. 使用 `json.load` 读取数据。
3. 文件顶层不是列表时，抛出 `ConversationFileError`。
4. JSON 语法损坏时，把底层 `JSONDecodeError` 转成更容易理解的 `ConversationFileError`。

完成后运行本课全部测试：

```bash
.venv/bin/python -m pytest demos/s01-l03-files-errors/tests/test_conversation_store.py -q
.venv/bin/python demos/s01-l03-files-errors/conversation_store.py
```

## 错误分类

| 情况 | 处理 | 原因 |
|---|---|---|
| 文件不存在 | 返回空列表 | 首次运行很正常，可以自动恢复 |
| 空消息 | 不保存 | 类型合法，但没有有效内容 |
| 消息结构错误 | `ValueError` | 调用方传入的数据违反约定 |
| JSON 文件损坏 | `ConversationFileError` | 不能假装读到了正常历史 |

## 独立变式挑战

给保存结果增加顶层字段 `version`，文件结构变为：

```json
{
  "version": 1,
  "messages": []
}
```

先修改测试写下预期，再修改实现。思考：旧版列表格式是否继续支持？你的选择要写进复盘。

## 完成标准

- 本课自动测试全部通过。
- 能解释模块、函数、参数和返回值各自解决什么问题。
- 能解释为什么文件不存在与文件损坏不能采用相同处理。
- 完成独立变式挑战。
- 填写 `reflection.md` 的故障定位记录。
