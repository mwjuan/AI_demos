# S01-L04：提示词、上下文与结构化消息

这一课学习如何把发给模型的信息组织成结构化消息。我们会分成几个很小的步骤，每次只增加一个概念。

## 今天的目标

- 区分 `system`、`user`、`assistant` 三种角色。
- 理解上下文是模型本次请求中实际收到的消息，不等于模型永久记忆。
- 只改变一个提示词变量并比较结果。
- 要求模型返回 JSON，并在 Python 中验证结果。

## 第一轮：只认识角色

先阅读 `message_roles.py` 中的 `SAMPLE_CONVERSATION`，暂时不要修改代码。

三种角色可以先这样理解：

| 角色 | 谁提供 | 作用 |
|---|---|---|
| `system` | 应用开发者 | 设定任务、行为边界和回答风格 |
| `user` | 当前用户 | 提出本轮实际问题或要求 |
| `assistant` | 模型 | 保存模型此前的回答，构成多轮上下文 |

需要注意：角色只是消息的来源和用途，不保证内容一定真实。历史中的错误回答仍然可能影响下一轮。

先回答三个问题：

1. 哪条消息规定了回答风格？
2. 哪条消息是用户当前想解决的问题？
3. 如果删除最后一条 `assistant` 消息，模型还能看到此前的回答吗？

## 第二轮：构造两条消息

完成 `build_messages(user_input)`，返回一条 `system` 消息和一条 `user` 消息。这里只需要类型检查、`strip()` 和列表/字典，不调用模型。

完成后运行：

```bash
.venv/bin/python -m pytest demos/s01-l04-prompts-context/tests/test_message_roles.py -q
```

后续步骤会在第一轮和第二轮掌握后再继续。

## 第三轮：单变量提示词实验

运行 `prompt_experiment.py`。两次请求使用相同的用户问题和模型，只改变 `system` 提示词：一次要求简洁回答，一次要求用生活化比喻向小学生解释。

```bash
.venv/bin/python demos/s01-l04-prompts-context/prompt_experiment.py
```

观察两组回答的长度、用词和是否出现比喻。模型输出带有随机性，因此重点观察整体倾向，不要求每个字都固定。

如果模型服务暂时不可用，保留脚本并记录外部原因，然后先进行下面的离线解析练习。

## 第四轮：解析结构化 JSON

模型返回的内容通常先表现为字符串，即使这个字符串看起来像 JSON，也需要用 `json.loads()` 才能转换成 Python 数据。

完成 `structured_output.py` 中的 `parse_json_object()`：

1. 输入必须是字符串。
2. 用 `json.loads(text)` 解析；捕获 `json.JSONDecodeError` 并转成 `ValueError`。
3. 解析结果必须是字典，列表等其他合法 JSON 也要拒绝。

```bash
.venv/bin/python -m pytest demos/s01-l04-prompts-context/tests/test_structured_output.py -q
```

解析成功只说明 JSON 语法正确，不代表数据结构符合应用要求。下一步完成 `parse_study_card()`，继续验证 `term` 和 `definition` 都是清理后非空的字符串。

最后运行一次真实结构化输出实验：

```bash
.venv/bin/python demos/s01-l04-prompts-context/structured_experiment.py
```

脚本会先显示模型原始文本，再使用 `parse_study_card()` 验证 JSON 语法和字段结构。即使提示词要求“只返回 JSON”，应用仍然必须校验。
