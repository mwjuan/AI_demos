# S01-L06：Streamlit 聊天机器人

这一课把前面完成的模型调用、消息结构、异常处理和本地会话组合成一个多轮聊天界面。

## 今天的目标

- 理解 Streamlit 每次交互都会重新运行脚本。
- 使用 `st.session_state` 保存当前标签页的聊天记录。
- 展示 `user` 和 `assistant` 消息。
- 清空聊天时只删除消息，不误删模型和参数设置。
- 在服务端读取模型配置和密钥，不向浏览器暴露密钥。
- 把模型调用错误转换成用户能理解的界面提示。

## 第一轮：会话状态

打开 `chat_state.py`，完成：

1. `initialize_messages(state)`：不存在 `messages` 时创建一个新列表；已经存在时保留原列表。
2. `clear_messages(state)`：只把 `messages` 设置为空列表，保留其他状态。
3. 不同会话必须获得不同的消息列表，不能共享可变默认值。

运行：

```bash
.venv/bin/python -m pytest demos/s01-l06-streamlit-chat/tests/test_chat_state.py -q
```

本轮使用普通字典模拟 `st.session_state`。先验证状态逻辑，再接入 Streamlit 界面。

## 第二轮：追加消息

完成 `append_message(state, role, content)`：

1. 只允许 `user` 和 `assistant` 两种角色。
2. 内容必须是非空字符串，并清理前后空白。
3. 复用 `initialize_messages()`，不要重复初始化逻辑。
4. 按顺序保存消息，保证下一次模型请求能获得完整上下文。

## 第三轮：接入 Streamlit 界面

完成 `app.py` 中的三个 TODO：

1. 在侧边栏提供“清空聊天”按钮，只清除 `messages`。
2. 使用 `st.chat_message()` 按原顺序显示历史消息。
3. 使用 `st.chat_input()` 接收输入，追加用户消息后调用 `st.rerun()`。

运行界面：

```bash
.venv/bin/streamlit run demos/s01-l06-streamlit-chat/app.py
```

这一轮只验证界面和会话状态，暂时不会调用模型。

## 第四轮：构造多轮模型请求

完成 `model_chat.py` 中的 `build_ollama_payload(model, messages)`：

1. 验证模型名和消息列表。
2. 保留全部 `user`、`assistant` 历史，而不只是最新问题。
3. 创建消息快照，避免请求发送期间会话状态被修改。
4. 使用非流式响应并关闭思考模式。

运行：

```bash
.venv/bin/python -m pytest demos/s01-l06-streamlit-chat/tests/test_model_chat.py -q
```

## 第五轮：验证模型响应

完成 `extract_assistant_reply(data)`：

1. 顶层响应必须是字典。
2. `done_reason` 必须为 `stop`。
3. `message.content` 必须是非空字符串。
4. 返回清理后的回答；不完整结果抛出 `OllamaChatError`。

这一步把“HTTP 成功”和“回答可以展示”分开判断。

## 第六轮：发送真实 Ollama 请求

打开 `model_chat.py`，完成 `request_ollama_reply(model, messages)`：

1. 复用 `build_ollama_payload()` 构造包含完整历史的请求体。
2. 把请求发送到 `http://127.0.0.1:11434/api/chat`。
3. 使用 `httpx.Client(trust_env=False)`，避免本机请求被环境代理转发。
4. 将连接失败、超时、HTTP 错误和无效 JSON 转换为可读的 `OllamaChatError`。
5. 复用 `extract_assistant_reply()` 验证并返回完整回答。

先只运行第一个新测试：

```bash
.venv/bin/python -m pytest \
  demos/s01-l06-streamlit-chat/tests/test_model_chat.py::test_request_ollama_reply_posts_history_and_returns_answer -q
```

它现在应该因 `NotImplementedError` 失败。先让这一个测试通过，不要一次完成所有异常分支。

## 第七轮：在 Streamlit 展示回答与错误

第六轮通过后，再修改 `app.py`：

1. 在侧边栏提供 Ollama 模型名，默认为 `qwen3:4b`。
2. 提交后立即展示用户问题。
3. 成功时保存并展示助手回答。
4. 失败时使用 `st.error()` 展示原因，不把错误文本写入历史。

启动前确认 Ollama 正在运行，并且已安装侧边栏中填写的模型：

```bash
ollama list
.venv/bin/streamlit run demos/s01-l06-streamlit-chat/app.py
```

完成后，用下列方式验证两条界面路径：

- 正常路径：启动 Ollama 并使用已安装模型提问，界面展示助手回答。
- 错误路径：在侧边栏输入不存在的模型名，界面展示 Ollama 返回的 HTTP 错误。
