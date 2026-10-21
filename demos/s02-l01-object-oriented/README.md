# S02-L01：面向对象与 Python 工程结构

## 当前教学方式（2026-10-21 更新）

按学习者要求，后续以大模型请求流程与设计为主，代码由助手生成与验证，见[教学模式](../../notes/LEARNING-MODE.md)。下方逐轮手写任务保留为历史讲义，不再要求学习者补代码。第十二轮页面整合已通过模拟验收；当前讨论请求中的上下文、状态和失败重试，不以配置快照手写变式阻塞课程，也未因此自动标记整课通过。

## 前置知识

已通过 S01-GATE，能使用函数、字典、模块和异常，能解释主线聊天应用的数据流。

## 学习目标

- 区分类、实例、属性和方法，解释 `self` 与 `__init__`。
- 用配置对象管理模型来源、两个模型名和超时；不同实例互不影响。
- 逐步用会话类管理消息，用提供商类封装调用；页面负责交互，文件模块负责存取。
- 重构后保留 S01 的多轮历史、错误展示、模型切换、清空及保存/恢复行为。

## 学习安排

建议概念 40 分钟、核心编码 100 分钟、实验排错 60 分钟、复盘 40 分钟。按轮推进，先完成一轮再继续。

## 第一轮：模型配置类（实现已验证）

过去使用 `st.session_state["timeout"]` 保存设置。现在先脱离页面，用 `config.timeout` 表示同一类数据。

打开 `model_config.py`，只完成 `__init__`：

1. 在当前实例上保存四个属性：`provider`、`local_model`、`cloud_model`、`timeout`。
2. 默认值依次为 `ollama`、`qwen3:4b`、`qwen-plus`、`120.0`。
3. 不调用模型，不操作 Streamlit，也不读写文件。

在本目录进入 Python 交互环境：

```bash
cd /Users/mwj/shgbit/study/ai/demos/s02-l01-object-oriented
/Users/mwj/shgbit/study/ai/.venv/bin/python
```

执行下列检查代码。它是使用示例，不是类的实现答案：

```python
from model_config import ModelConfig

first = ModelConfig()
second = ModelConfig()
print(first.provider, first.local_model, first.cloud_model, first.timeout)
first.timeout = 180.0
print(first.timeout, second.timeout)
```

预期第一行是四个默认值，第二行是 `180.0 120.0`。解释为什么修改 `first` 不影响 `second`。

## 第二轮：方法与恢复默认设置（实现已验证）

完成 `reset()`，让当前实例的四个属性恢复默认值，不创建一个替代实例返回给调用者。

分别修改四个属性，调用 `first.reset()` 后检查默认值；再次调用不应报错。调用前保存 `original = first`，调用后检查 `original is first` 为 `True`，说明仍是同一个对象。

解释 `config.reset()` 与只修改一个 `config.timeout` 各自影响什么。

## 第三轮：会话实例与可变属性（初始化与清空实现已验证）

打开 `chat_session.py`，先只完成 `ChatSession.__init__`，使每个新实例都有自己的空消息列表属性 `messages`。`clear()` 留到下一步。

在本课目录的 Python 交互环境中检查：

```python
from chat_session import ChatSession

first = ChatSession()
second = ChatSession()
first.messages.append({"role": "user", "content": "你好"})
print(first.messages)
print(second.messages)
print(first.messages is second.messages)
```

预期第一个列表含一条消息，第二个为空，最后输出 `False`。`is` 判断是否为同一个对象。这里直接追加消息仅用于观察列表是否独立，后续将通过方法复用既有消息校验。

思考：两个空列表的内容可以相同，但为什么不应该让两个会话共用同一个列表？

学习者已完成初始化及 `clear()`；运行验证确认实例列表独立，重复清空及清空后追加正常。当前 `clear()` 使用 `self.messages = []`。继续理解以下引用行为：

```python
chat = ChatSession()
chat.messages.append({"role": "user", "content": "你好"})
history = chat.messages
chat.clear()
print(chat.messages)
print(history)
```

先判断两个输出，再解释：`history` 保存的是旧列表的引用，并不会随着 `chat.messages` 重新赋值而自动指向新列表。后续消息快照练习会进一步处理列表与字典的引用。

## 第四轮：通过方法追加消息（实现已验证）

完成 `ChatSession.append_message(self, role, content)`，沿用第一阶段的消息验证规则：

1. `role` 只允许 `user` 或 `assistant`，否则抛出 `ValueError`。
2. `content` 必须是字符串，清理首尾空白后不能是空字符串，否则抛出 `ValueError`。
3. 所有验证通过后，创建包含 `role` 和清理后 `content` 的消息字典，追加到当前实例的 `messages`。
4. 返回刚追加的消息字典；任何非法输入都不能改变已有历史。

使用示例：

```python
chat = ChatSession()
message = chat.append_message("user", "  你好  ")
print(message)
print(chat.messages)
```

预期返回 `{"role": "user", "content": "你好"}`，历史中含这一条消息。调用时只传两个参数，Python 会把 `chat` 自动作为 `self` 传入。

分别尝试非法角色 `system`、数字内容 `123` 和纯空白内容，确认抛出 `ValueError` 且已有历史保持。先完成追加方法，再继续消息快照。

## 第五轮：返回独立的消息快照（实现与引用判断已验证）

当页面或模型调用需要读取历史时，提供 `snapshot()` 方法返回当时的消息副本，避免调用方修改副本时连带改变会话内部历史。

要求：

1. 返回一个新列表，保留原消息的顺序和内容；空历史返回空列表。
2. 列表中的每条消息也必须是新字典。
3. 修改快照中消息的内容、追加或删除快照里的消息，都不能影响内部历史。
4. 后续追加或清空内部历史，已经取得的快照保持原样。

提示：只返回 `self.messages` 会共用列表；只复制外层列表，仍会共用其中的消息字典。本课消息字典只有 `role`、`content` 两个字符串字段，复制每条字典即可，不需要引入通用的递归复制工具。可以使用熟悉的 `for` 循环逐条构造结果。

完成后检查：

```python
chat = ChatSession()
chat.append_message("user", "你好")
saved = chat.snapshot()
saved[0]["content"] = "改过的内容"
saved.append({"role": "assistant", "content": "额外消息"})
print(chat.messages)
```

预期内部历史仍然只有 `{"role": "user", "content": "你好"}` 这一条。继续检查空历史、反复取得快照、后续追加及清空的路径。

学习者实现的双层复制已通过上述运行验证，并正确判断只复制外层列表时修改字典会影响原历史。准确原因是新旧列表仍引用同一个消息字典。学习者已删除 `return` 后不可达的骨架异常语句。

## 第六轮：提供商对象复用模型调用（本地实现已验证）

目前 `ModelConfig` 管理设置，`ChatSession` 管理消息。新增 `OllamaProvider` 负责使用设置调用本地模型。提供商持有配置对象，这种对象之间的组合可以让已有能力配合工作。

完成 `providers.py` 的两个方法：

1. `__init__(self, config)`：将传入的配置对象保存为 `self.config`，不额外创建或复制配置对象。
2. `reply(self, messages)`：复用已导入的 `request_ollama_reply(model, messages, *, timeout=120.0)`，模型名取当前配置的 `local_model`，超时取当前配置的 `timeout`，消息传入完整 `messages`，返回原函数的回答。`timeout` 必须按关键字传入。

模型名和超时在每次 `reply()` 时读取，所以之后修改或恢复配置也能在下一次调用生效。旧函数负责请求与响应校验；提供商将错误继续交给调用方，不把错误文本变成回答，不自行修改聊天历史。

使用关系示例：

```python
from model_config import ModelConfig
from chat_session import ChatSession
from providers import OllamaProvider

config = ModelConfig()
chat = ChatSession()
provider = OllamaProvider(config)
print(provider.config is config)  # 应为 True
```

先实现并交由助手用模拟请求检查参数转交、配置后续修改、回答返回与错误路径；无需为了本轮验证发出真实模型请求。本地提供商通过后，再增加云端提供商与来源选择。

本地提供商已通过模拟请求验证，包括修改和恢复配置后参数生效、回答返回、异常传递及历史保留。

## 第七轮：云端提供商与统一方法（实现已验证）

完成同一文件中的 `CloudProvider`：

1. 构造方法保存传入的配置对象。
2. `reply(self, messages)` 调用已导入的统一入口 `request_reply(provider, model, messages, *, timeout=120.0)`，固定来源为 `cloud`，使用当前 `self.config.cloud_model`、完整消息列表和当前超时，返回回答。

此处复用统一入口，是因为它已经负责读取云端环境配置、创建客户端及关闭客户端；直接调用底层 `request_cloud_reply` 则需要另外提供客户端。网络错误与响应验证继续复用旧实现。

两种提供商都接受相同的 `reply(messages)` 调用。调用方可以先选对象，再统一调用方法；本轮先完成云端类，下一步再实现来源选择。无需继承或基类即可做到这一点。

完成后以模拟请求验证固定来源、云端模型名、历史与超时、配置后续修改和恢复、回答及错误路径，再进入来源选择与整合。

云端类已通过模拟验证，包括固定来源、配置参数转交与后续变更、回答返回、异常传递、历史保留和故障后继续调用。未发出真实模型请求。

## 第八轮：选择对象，再统一调用（实现已验证）

完成 `providers.py` 文件末尾的普通函数 `create_provider(config)`：

1. `config.provider` 为 `ollama` 时，返回使用该配置的 `OllamaProvider` 实例。
2. 为 `cloud` 时，返回使用该配置的 `CloudProvider` 实例。
3. 其他来源抛出 `ValueError`，错误信息包含不支持的来源。
4. 返回对象，不是类本身，也不是回答；选择时不发出模型请求。

该函数放在类外面，因此没有 `self` 参数。它把选择逻辑集中在一个地方，让页面或命令行统一调用对象的 `reply()`。

使用示例：

```python
from model_config import ModelConfig
from providers import create_provider

config = ModelConfig()
provider = create_provider(config)
print(type(provider).__name__)  # OllamaProvider

config.provider = "cloud"
provider = create_provider(config)
print(type(provider).__name__)  # CloudProvider
```

来源变化后要重新选择对象，原来的本地对象不会自动变成云端对象。模型名和超时则继续从共享的配置对象实时读取。

完成后先以模拟请求验证两种返回类型、配置引用、未知来源拒绝、选择时不请求及统一调用，再接主线应用。

选择函数及统一调用的模拟验证已通过。修改来源后须重新选择对象，原对象的类型保持不变。

## 第九轮：接入主线命令行（功能模拟验收已通过）

主线 `knowledge-assistant/cli.py` 已补充三个模块的导入，原问答逻辑仍由学习者重构。先保持一次提问、一次回答，不增加循环或新的命令行参数。

在 `main()` 中：

1. 创建 `ModelConfig` 和 `ChatSession` 实例，替换分散的来源、模型、超时变量与手动消息列表。
2. 读取输入；在 `try` 中通过会话的 `append_message()` 验证并追加用户消息。
3. 使用 `create_provider(config)` 选择对象，再通过 `reply(chat.snapshot())` 获取回答。
4. 保留 `ValueError`、`RuntimeError` 的错误提示；空白问题必须在请求前拒绝。
5. 成功时通过会话方法追加助手回答，并打印 `回答：...`；错误文本不能加入历史。

不要绕过会话方法直接操作消息列表，也不要调用旧的 `request_reply()`；旧导入在不再使用后可删除。

完成后交由助手运行实际 `main()`，模拟输入与模型返回，检查正常问答、空白拒绝、参数错误、请求失败、历史和快照行为；之后再由学习者验证真实调用。命令行验收后才接页面，主线重构尚未完成。

本轮首次检查：配置、会话、快照及已有正常/错误行为通过模拟验证；提供商接入待修正。当前仍直接调用 `request_reply()` 且固定读取本地模型，模拟云端配置时会传错模型名。下一步改为通过 `create_provider(model_config)` 选择对象，并调用其 `reply(messages_snapshot)`，由提供商读取对应设置。

修正后复查已通过：两种来源使用正确提供商、模型、超时和独立快照；成功保存回答；空白拒绝、未知来源及请求失败路径符合要求，旧入口未调用。本次使用模拟模型回答，真实调用仍待学习者验证。旧导入、未用变量和旧注释可在整理阶段删除。

## 第十轮：页面重跑与对象生命周期（修正后已验证）

`knowledge-assistant/app.py` 已补充新类导入及任务注释。先只完成标题下方的对象初始化，不改设置、聊天或文件功能：

1. 若 `st.session_state` 中没有 `model_config`，创建 `ModelConfig()` 保存到该键。
2. 若没有 `chat_session`，创建 `ChatSession()` 保存到该键。
3. 每次运行都从这两个键取出对象，分别赋给局部变量 `model_config` 和 `chat_session`，供后续代码使用。

Streamlit 每次交互都会重跑脚本。如果每次都直接执行构造方法并覆盖状态，修改过的设置及聊天历史会丢失。只在键不存在时创建，才能保留同一页面会话中的对象。

本轮已有界面仍使用旧状态，两套对象尚未接通。完成后先验证两次运行间的对象身份、设置和消息保留，并确认新页面会话中的对象彼此独立；随后逐步将聊天和设置接入，最后整合保存/加载及整理模块。

首次检查：条件初始化已实现，AppTest 验证对象及其内容在重跑和控件交互后保留，不同页面会话互相独立。尚缺第三步：在两个条件判断外，将保存的对象取出赋给局部变量。已有控件仍未与新对象同步，尚不能将页面整合标记为完成。

补充引用后的复查：两行取值被放在条件初始化之前，导致新会话缺键报错。需调整为“先条件创建，再在条件外取值”；已有状态的页面正常不代表首次加载也正常。

修正顺序后已通过 AppTest：全新页面正常加载，重跑及控件交互保留对象与内容，不同会话的对象独立。

## 第十一轮：控件设置与提供商接通（实现已验证）

先保留已经验证过的控件、模型切换与文件逻辑，只调整配置同步和请求调用：

1. 在超时控件创建之后，将当前控件值同步到配置对象：`provider` 对应 `model_config.provider`；`models["ollama"]` 对应 `local_model`；`models["cloud"]` 对应 `cloud_model`；`timeout` 对应 `model_config.timeout`。每次重跑都同步，不放在首次初始化条件中。
2. 在原请求的 `try` 中，通过 `create_provider(model_config)` 选择提供商对象，变量命名为 `model_provider`，避免覆盖来源字符串 `provider`。
3. 用 `model_provider.reply(messages)` 取代直接调用旧 `request_reply()`，保留已有错误和成功分支。本轮暂用原来的完整历史列表，下一轮再统一接入 `ChatSession` 和其快照，避免一部分逻辑使用新历史、另一部分使用旧历史。

完成后模拟验证：本地与云端参数、模型名分别保留、超时变更、恢复默认后请求、完整多轮历史及错误后继续聊天。当前 `chat_session` 对象仍未用于页面历史，不将该步视为全部页面重构完成。

以上路径已通过 AppTest 模拟验证；恢复默认与清空保持预期行为，已有对话文件未改写。本次未发出真实模型请求。

## 第十二轮：所有历史操作使用同一个会话对象（模拟验收已通过）

将页面历史统一交给 `chat_session`，把这些路径一起接通：

1. 清空按钮调用 `chat_session.clear()`，然后重跑。历史展示可以让 `messages = chat_session.snapshot()`，用于遍历显示；它只是当时的副本。
2. 输入处理的 `try` 中，先调用 `chat_session.append_message("user", prompt)`，再展示用户消息。验证失败由已有 `except ValueError` 展示，不能在 `try` 外追加导致异常漏出。
3. 选择提供商后，调用 `model_provider.reply(chat_session.snapshot())`。快照必须在追加用户问题之后取得，才能包含最新问题；不要将展示时取得的旧快照直接作为本轮请求。
4. 成功分支通过 `chat_session.append_message("assistant", reply)` 保存回答并展示，失败不追加助手消息。
5. 保存按钮读取当前会话快照；空历史仍只提示，不覆盖文件。继续复用 `save_messages` 与既有错误提示。
6. 加载按钮先调用 `load_messages`；没有有效消息时沿用原提示与历史。成功读到消息后，创建临时 `ChatSession` 并逐条通过 `append_message` 验证、填充，全部成功后才替换 `st.session_state["chat_session"]` 并重跑。这样任何读取或验证失败都能保留原会话。继续复用既有异常捕获。

完成后页面历史不再依赖 `initialize_messages`、`clear_messages` 或旧的模块级 `append_message`，可移除相关旧导入。`request_reply` 的旧导入也已不再使用。模型设置同步和切换逻辑保持当前实现。

先以新页面会话检查多轮聊天、清空、空白输入拒绝、请求快照隔离、错误后恢复、保存/加载及文件失败路径。模拟文件操作须使用临时目录或模拟函数，避免改写已有对话文件。真实调用与模块整理仍待后续验证，本轮完成不代表整课通过。

2026-10-21 首次检查：清空对象、展示快照及预先填充会话后的保存已验证。聊天仍向快照追加，导致会话为空、重跑丢失问答；加载仍清空正式会话并写入旧状态，未构造临时会话，验证失败会丢失原历史。继续完成上述第 2、3、4、6 项，再复查。本次仅使用模拟回答和临时文件，已有对话文件保持原样。

同日第二次检查：聊天追加与最新请求快照已修正，两轮历史、重跑、快照隔离、错误后恢复和保存/清空通过模拟验证。仍需将用户追加移入 `try`，避免纯空白输入导致页面异常；加载改用临时会话，删除先修改或清空正式会话及调用不存在的 `append_messages()` 的逻辑，全部成功后才替换状态对象。本轮尚未通过。

同日第三次检查已通过：用户追加位于 `try` 内，加载使用临时会话并在全部验证成功后替换状态对象。AppTest 的 12 组场景覆盖多轮历史与重跑、空白拒绝、请求快照隔离、两类模型请求错误及恢复、两种来源的参数和设置恢复、保存及重复清空、加载成功后的继续聊天、重复加载、中途验证失败保留原对象与全部历史、损坏/缺失/空文件，以及读写错误。未创建旧 `messages` 状态；全部模型请求为模拟，文件操作使用临时目录，已有对话文件未改变。下一步为配置快照独立变式，整课尚未通过。

## 后续核心编码

各类逐轮完成后，继续准备与验证：

1. 会话类：追加、清空、获取消息快照；复用既有消息验证规则。
2. 提供商类：让本地与云端对象提供一致的调用方法，复用已验证的请求函数。
3. 工程整合：页面持有配置和会话对象，按来源选择提供商；CLI 与页面复用这些模块。

配置、会话、提供商与选择函数已通过当前检查，主线命令行及页面设置、请求、会话历史和文件操作已通过模拟验收。真实调用与模块整理仍待完成。本课不提前引入数据库、流式响应或 Web API。

## 必做实验与排错

- 创建两个配置实例，只修改一个，确认彼此独立。
- 比较函数内的局部变量和实例属性：为什么 `timeout = 120.0` 不能代替 `self.timeout = 120.0`？
- 整合时验证 Streamlit 重跑后仍保留当前对象；仅在不存在时初始化，避免每次交互都恢复默认值。
- 模型请求采用模拟回答先检查历史、设置与错误路径，再由学习者验证真实调用。

## 原独立编码变式（不再作为过关要求）

原练习为 `ModelConfig` 增加配置快照方法，已取消学习者手写要求；该方法尚未实现，以后确有功能需要时由助手生成与验证。当前独立设计练习改为：用户问题已进入历史、模型请求超时，重试时如何保持消息与请求状态一致？

## 完成标准与证据

- 配置、会话、提供商及页面职责清晰，提交类关系和一次请求的数据流说明。
- 主线重构后通过正常聊天、完整历史、错误展示与恢复、模型设置、清空、保存/加载检查；保留验证结果。
- 能解释请求流程与失败处理设计，完成独立设计练习并记录复盘；实现与代码整理由助手负责。只有代码模拟验收通过不能标记整课通过。
