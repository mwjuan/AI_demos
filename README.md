# AI Learning Lab

这是一个以大模型应用流程与设计为主、以“个人知识库助手”为持续项目的 AI 学习空间。代码由助手生成与验证，学习者重点理解需求、数据流、设计取舍和验收方法。课程按照六个能力阶段推进，不限定周数；完成当前阶段的实验、设计解释和闯关验收后进入下一阶段。当前分工与衔接见[教学模式](./notes/LEARNING-MODE.md)。

## 当前进度

- [x] 工作区初始化
- [x] [`S01-L01`](./demos/s01-l01-first-api/README.md)：从 Python 发出第一次模型请求
- [x] [`S01-L02`](./demos/s01-l02-python-data/README.md)：Python 数据、控制流与容器
- [x] [`S01-L03`](./demos/s01-l03-files-errors/README.md)：函数、模块、文件与异常
- [x] [`S01-L04`](./demos/s01-l04-prompts-context/README.md)：提示词、上下文与结构化消息
- [x] [`S01-L05`](./demos/s01-l05-ollama-local/README.md)：Ollama 与本地模型
- [x] [`S01-L06`](./demos/s01-l06-streamlit-chat/README.md)：Streamlit 聊天机器人
- [x] `S01-GATE`：入门阶段闯关
- [ ] [`S02-L01`](./demos/s02-l01-object-oriented/README.md)：面向对象与 Python 工程结构（实现已通过模拟验收，转入模型请求流程与失败处理设计）

第一阶段已通过，证据见[最终验收](./notes/S01-GATE.md)与[第六课复盘](./demos/s01-l06-streamlit-chat/reflection.md)。2026-10-19 核对学习者完成的“恢复默认设置”独立变式，页面模拟验证通过：默认设置、聊天与文件保留、重复恢复、来源切换及后续请求参数均符合要求；本次未发出真实模型请求。当前学习 `S02-L01`，配置类、会话类、两种提供商及来源选择已通过运行或模拟检查，主线命令行重构已通过两种来源及错误路径的模拟验收。2026-10-21 页面会话、最新请求快照及保存/加载通过 AppTest 模拟验收，包括空白拒绝和加载失败保留原历史；已有对话文件保持。同日按学习者要求改为流程与设计教学，取消手写配置快照变式的过关要求，当前讨论模型请求与超时重试设计；实现和代码整理由助手负责。真实调用、设计解释与复盘仍待完成，本课尚未完成。全部阶段、依赖和验收条件见[课程地图](./notes/ROADMAP.md)。

## 六阶段导航

| 阶段 | 核心能力 | 阶段成果 | 课程入口 |
|---|---|---|---|
| S01 AI 大模型开发入门 | Python 基础、模型 API、本地模型与提示词 | 命令行与 Streamlit 聊天机器人 | [进入 S01](./curriculum/stage-01/README.md) |
| S02 大模型应用开发 | Python 进阶、数据处理、Web API 与结构化输出 | 流式 Web 聊天与学习卡片应用 | [进入 S02](./curriculum/stage-02/README.md) |
| S03 大模型核心开发技术 | 机器学习、PyTorch、NLP 与 Transformer | 文本分类、Embedding 检索和评估报告 | [进入 S03](./curriculum/stage-03/README.md) |
| S04 大模型智能体开发 | RAG、LangGraph、工具、MCP 与可观测性 | 可引用、可评估、可恢复的知识库智能体 | [进入 S04](./curriculum/stage-04/README.md) |
| S05 大模型定制开发 | 微调、量化、部署、多智能体与生产治理 | 垂直模型与企业级多智能体助手 | [进入 S05](./curriculum/stage-05/README.md) |
| S06 大模型算法进阶 | 算法、CV、多模态、扩散模型与强化学习 | 多模态知识助手 | [进入 S06](./curriculum/stage-06/README.md) |

课程目录总览见[课程骨架](./curriculum/README.md)，参考学习路线的逐项映射见[路线覆盖矩阵](./curriculum/COVERAGE.md)。

## 每课学习契约

每课以一个真实场景展开：需求与成功条件、流程设计、方案取舍、助手实现与实验、学习者验收。按理解程度推进，不要求固定编码时长。

每课必须同时满足：

1. **能设计**：面对需求能拆出流程、边界和关键取舍。
2. **能解释**：能够用自己的话解释数据流、关键概念和失败原因。
3. **能验收**：能提出正常、失败和边界场景，并判断实验结果；实现和必要自动检查由助手完成。
4. **有证据**：保存代码、测试结果、实验记录和 `reflection.md`。

阶段闯关还要求完成主线项目增量、独立设计挑战和数据流解释验收。助手生成实现不等于学习者已理解；手写代码不作为过关条件。不能稳定复现结果时，不以“看完课程”视为完成。

## 目录约定

```text
curriculum/             六阶段课程骨架与路线覆盖矩阵
demos/                  独立、小而明确的课程练习
knowledge-assistant/    六阶段持续演进的主线应用
notes/                  课程地图、概念笔记和复盘
evals/                  固定评估集、基线与实验报告
docs/                   原始课程大纲与学习路线
```

## 快速开始

项目要求 Python 3.11 或更高版本：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
```

运行已经完成的 `S01-L01`：

```bash
python demos/s01-l01-first-api/scripts/check_progress.py
python -m s01_l01_first_api direct
python -m s01_l01_first_api.experiment
```

## 模型与安全约定

课程默认使用 DeepSeek，同时支持通义千问和 OpenAI；后续代码必须沿用可切换的提供商配置。密钥只放在本地 `.env`，不提交到版本库、不写入前端、不出现在日志、截图和实验结果中。本地单用户实现优先，云部署、账号权限和大规模基础设施在高阶阶段再引入。
