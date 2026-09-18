# S01-L01：从 Python 发出第一次模型请求

这是六阶段路线的第一课，只聚焦一条数据链路：命令行输入提示词，Python 服务端代码携带密钥调用模型，程序读取回答和用量并显示结果。

```text
你输入的问题 → Python 程序 → 模型 API → 响应文本与用量 → 终端
```

## 开始前

在仓库根目录创建隔离环境并安装依赖：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

复制配置文件，并把自己的 API 密钥写入 `.env`：

```bash
cp demos/week-01-first-api/.env.example demos/week-01-first-api/.env
```

`.env` 已被忽略，不会进入版本库。不要把密钥写入源代码、截图或聊天消息。

如果当前网络需要 Clash Verge，在 `.env` 中增加实际混合代理地址：

```env
AI_PROXY_URL=http://127.0.0.1:7897
```

端口以 Clash Verge 设置为准。你的当前配置使用 `7897`；设置后 Python SDK 会显式通过 Clash 访问模型服务。

默认配置使用 **DeepSeek**。也可以把 `AI_PROVIDER` 改为 `qwen` 或 `openai`，分别切换到 **通义千问** 或 **OpenAI**。DeepSeek 和千问都提供 OpenAI 兼容接口，因此三个提供商可以使用同一个 Python 客户端学习统一调用方式。

默认选项：

| 提供商 | `AI_PROVIDER` | 默认模型 | 密钥变量 |
|---|---|---|---|
| DeepSeek | `deepseek` | `deepseek-flash` | `DEEPSEEK_API_KEY` |
| 通义千问 | `qwen` | `qwen-plus` | `DASHSCOPE_API_KEY` |
| OpenAI | `openai` | `gpt-5.6-luna` | `OPENAI_API_KEY` |

千问的新业务空间可能提供带 `WorkspaceId` 的专属地址。若控制台给出了该地址，把它完整填写到 `QWEN_BASE_URL`；密钥和地址必须属于同一地域。

## 你的核心任务

打开 `src/week01_first_api/model.py`，实现 `call_model(prompt, client=..., model=...)` 中标出的 TODO。要求：

1. 使用已经传入的 `client` 调用兼容的 Chat Completions API，不能在函数里读取或打印密钥。
2. 使用 `model` 和 `prompt` 参数，不写死问题。
3. 返回统一结果：`text`、`request_id`、`model` 和 `usage`。
4. `usage` 至少包含 `input_tokens`、`output_tokens`、`total_tokens`；服务未返回某项时使用 `None`。
5. 捕获异常后抛出包含可行动提示的新错误，并使用异常链保留原异常。

官方参考：[DeepSeek 首次调用](https://api-docs.deepseek.com/)；[千问 OpenAI 兼容接口](https://help.aliyun.com/zh/model-studio/qwen-api-via-openai-chat-completions)；[OpenAI Chat Completions](https://platform.openai.com/docs/api-reference/chat/create)。

完成后先运行不联网的检查：

```bash
python demos/week-01-first-api/scripts/check_progress.py
pytest
```

再发出真实请求：

```bash
python -m week01_first_api direct
python -m week01_first_api audience
python -m week01_first_api example
```

最后一次运行三组实验并保存结果：

```bash
python -m week01_first_api.experiment
```

实验结果会写入当前目录的 `results/`。它只保存提示词、回答和用量，不保存密钥。

## 三个提示词只改变一个维度

- `direct`：直接要求解释 Python 闭包。
- `audience`：增加读者背景和表达要求。
- `example`：在相同读者要求上增加必须包含的例子。

不要在第一次实验前修改这些提示词。先观察，再提出假设，然后只改一个变量重新实验。

## 失败实验

正常调用成功后，临时移除当前提供商的密钥，确认程序在发出请求前给出清晰错误。然后恢复密钥，并把对应的 `DEEPSEEK_MODEL`、`QWEN_MODEL` 或 `OPENAI_MODEL` 临时改成一个不存在的名称，观察服务端错误与本地提示。不要在复盘中粘贴完整错误对象，以免意外包含敏感信息。

## 本课验收

- 进度检查和 `pytest` 通过。
- 三种提示词均得到响应，且终端能看到 token 用量。
- `results/` 中有一次完整对比实验。
- 完成 `reflection.md`，能解释提示词差异、幻觉风险和密钥为何不能放进浏览器。
