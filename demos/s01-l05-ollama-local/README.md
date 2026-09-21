# S01-L05：Ollama 与本地模型

这一课学习如何从 Python 调用本机 Ollama，并用固定测试集比较本地模型与云端模型的质量、速度和隐私边界。

## 今天的目标

- 区分 Python 客户端、Ollama 服务和模型文件。
- 通过 `http://127.0.0.1:11434` 调用本地模型。
- 读取回答、结束原因、耗时和 token 统计。
- 区分冷启动耗时与热请求耗时。
- 用同一测试集比较本地模型与云端模型。
- 记录超时、截断和指令未遵循等失败样本。

## 当前环境

- Ollama：`0.34.2`
- 本地模型：`qwen3:4b`
- 模型文件：约 2.5 GB
- 运行时占用：约 3.2 GB
- 处理器：Apple GPU

这些数字是本机观察值，不代表其他电脑一定相同。

## 数据流

```text
Python 客户端
    ↓ HTTP + JSON
Ollama 服务（127.0.0.1:11434）
    ↓ 加载和执行
qwen3:4b 模型
    ↓ 逐个生成 token
Ollama JSON 响应
    ↓
Python 提取文本和指标
```

## 第一轮：构造请求

打开 `ollama_client.py`，完成 `build_chat_payload(model, prompt)`。

要求：

1. `model` 和 `prompt` 必须是字符串。
2. 去除两者前后的空白。
3. 清理后不能为空。
4. 返回 Ollama `/api/chat` 所需的字典。
5. 本轮使用非流式响应，并关闭思考模式。

期望结构：

```python
{
    "model": "qwen3:4b",
    "messages": [{"role": "user", "content": "解释 Token"}],
    "stream": False,
    "think": False,
}
```

运行第一轮测试：

```bash
.venv/bin/python -m pytest demos/s01-l05-ollama-local/tests/test_ollama_client.py -q
```

通过后再进入真实 API 调用和响应指标解析。

## 第二轮：从 Python 请求 Ollama

完成 `request_chat(model, prompt, timeout=60.0)`：

1. 调用 `build_chat_payload()` 构造请求体。
2. 使用 `httpx.post(OLLAMA_CHAT_URL, json=payload, timeout=timeout)` 发送请求。
3. 调用 `response.raise_for_status()` 检查 HTTP 状态。
4. 连接失败时抛出包含“无法连接”的 `OllamaRequestError`。
5. 超时时抛出包含“超时”的 `OllamaRequestError`。
6. HTTP 错误中包含状态码，例如 `404`。
7. 使用 `response.json()` 解析结果，并确认顶层是字典。

异常捕获顺序很重要：`httpx.TimeoutException` 也是 `httpx.RequestError` 的子类，应先捕获更具体的超时异常。

## 第三轮：提取回答与性能指标

完成 `summarize_chat_response(data)`，返回：

```python
{
    "model": "qwen3:4b",
    "content": "模型回答",
    "done_reason": "stop",
    "total_seconds": 4.79,
    "load_seconds": 1.04,
    "prompt_tokens": 31,
    "output_tokens": 80,
    "tokens_per_second": 22.37,
}
```

Ollama 的时间字段使用纳秒。换算关系：

```text
1 秒 = 1,000,000,000 纳秒
```

生成速度只使用生成阶段的数据：

```text
tokens_per_second = eval_count / (eval_duration / 1_000_000_000)
```

当 `eval_duration` 为 0 时，速度返回 `0.0`，避免除零错误。`message.content` 缺失、不是字符串或清理后为空时，应抛出包含 `content` 的 `OllamaRequestError`。

## 已观察到的失败样本

- 现象：模型输出了分析过程，最终回答被截断。
- 证据：`done_reason` 为 `length`，`eval_count` 正好达到输出上限 80。
- 初步原因：当前模型没有按预期关闭思考输出，且 token 上限过小。
- 启示：请求成功不等于结果合格，应用仍需验证响应内容。

## 第四轮：拒绝不完整回答

完成 `require_complete_response(data)`：

1. 复用 `summarize_chat_response()` 获得摘要。
2. 只有 `done_reason == "stop"` 才返回摘要。
3. `length` 或缺少结束原因时抛出 `OllamaRequestError`。
4. 错误消息必须包含实际结束原因；缺失时应包含 `done_reason`，便于定位问题。

这一轮只判断生成是否完整。JSON 格式和业务字段属于下一层校验，不要全部塞进同一个函数。

## 完成证据

- [实验结果](experiment-results.md)：冷启动/热请求，以及本地与云端固定 JSON 任务对比。
- [学习反思](reflection.md)：速度指标、结果校验、结构化输出和隐私边界。
