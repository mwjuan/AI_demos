# AI Learning Lab

这是一个以 Python 实践为主、以“个人知识库助手”为持续项目的 AI 学习空间。课程按照六个能力阶段推进，不限定周数；只有完成当前阶段的代码、实验、复盘和闯关验收，才进入下一阶段。

## 当前进度

- [x] 工作区初始化
- [x] `S01-L01`：从 Python 发出第一次模型请求
- [ ] [`S01-L02`](./demos/s01-l02-python-data/README.md)：Python 数据、控制流与容器
- [ ] `S01-L03`：函数、模块、文件与异常
- [ ] `S01-L04`：提示词、上下文与结构化消息
- [ ] `S01-L05`：Ollama 与本地模型
- [ ] `S01-L06`：Streamlit 聊天机器人
- [ ] `S01-GATE`：入门阶段闯关

已完成的第 1 课保留原目录和命令，课程编号映射为 `S01-L01`。下一步从 `S01-L02` 开始；全部阶段、依赖和验收条件见[课程地图](./notes/ROADMAP.md)。

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

每课约 4 小时：40 分钟概念学习、100 分钟核心编码、60 分钟实验与排错、40 分钟复盘。时间是建议，不是过关条件。

每课必须同时满足：

1. **能运行**：必做实验和自动检查通过。
2. **能解释**：能够用自己的话解释数据流、关键概念和失败原因。
3. **能修改**：完成一个没有逐行答案的变式任务。
4. **有证据**：保存代码、测试结果、实验记录和 `reflection.md`。

阶段闯关还要求完成主线项目增量、独立挑战和口头解释验收。不能稳定复现结果时，不以“看完课程”视为完成。

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
python demos/week-01-first-api/scripts/check_progress.py
python -m week01_first_api direct
python -m week01_first_api.experiment
```

## 模型与安全约定

课程默认使用 DeepSeek，同时支持通义千问和 OpenAI；后续代码必须沿用可切换的提供商配置。密钥只放在本地 `.env`，不提交到版本库、不写入前端、不出现在日志、截图和实验结果中。本地单用户实现优先，云部署、账号权限和大规模基础设施在高阶阶段再引入。
