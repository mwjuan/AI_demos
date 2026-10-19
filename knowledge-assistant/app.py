"""S01 主线练习：复用课程模块，连接聊天页面与模型调用。"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st


# 入口移到主线目录后，仍然复用第六课的会话与模型模块。
project_dir = Path(__file__).resolve().parents[1]
lesson_dir = project_dir / "demos" / "s01-l06-streamlit-chat"
sys.path.insert(0, str(lesson_dir))

from chat_state import append_message, clear_messages, initialize_messages
from model_chat import request_reply

# 复用第三课的文件读写模块；主线入口与课程练习的目录层级不同。
store_dir = project_dir / "demos" / "s01-l03-files-errors"
sys.path.insert(0, str(store_dir))

from conversation_store import ConversationFileError, load_messages, save_messages


st.set_page_config(page_title="个人知识库助手", page_icon="📚")
st.title("📚 个人知识库助手")
if st.sidebar.button("恢复默认设置"):
    st.session_state["models"] = {
        "ollama": "qwen3:4b",
        "cloud": "qwen-plus",
    }
    st.session_state["model"] = "qwen3:4b"
    st.session_state["timeout"] = 120.0
    st.session_state["provider"] = "ollama"
    st.session_state["previous_provider"] = "ollama"
    model = "qwen3:4b"
    st.success("已恢复默认设置。")
    st.rerun()
    
# 第一步：先连接多轮聊天；模型设置、保存与恢复随后接入。
provider = st.sidebar.selectbox("模型来源", ["ollama","cloud"], key="provider")

if "models" not in st.session_state:
    st.session_state["models"] = {
        "ollama": "qwen3:4b",
        "cloud": "qwen-plus",
    }

models = st.session_state["models"]
# 第一次运行时，记住当前来源，并为模型输入框准备初始值。
if "previous_provider" not in st.session_state:
    st.session_state["previous_provider"] = provider
if "model" not in st.session_state:
    st.session_state["model"] = models[provider]

# 切换来源时，先保存旧模型名，再恢复新来源的模型名。
previous_provider = st.session_state["previous_provider"]
if provider != previous_provider:
    models[previous_provider] = st.session_state["model"]
    st.session_state["model"] = models[provider]
    st.session_state["previous_provider"] = provider

model = st.sidebar.text_input(
    "模型名称",
    key="model",
)

# 每次修改输入，都同步到当前来源对应的字典项。
models[provider] = model

if "timeout" not in st.session_state:
    st.session_state["timeout"] = 120.0
    
timeout = st.sidebar.number_input(
    "超时（秒）",
    min_value=1.0,
    max_value=600.0,
    step=10.0,
    key="timeout",
)

if st.sidebar.button("清空聊天"):
    clear_messages(st.session_state)
    st.rerun()

# TODO 1：初始化会话历史，将返回的列表保存到 messages。
messages = initialize_messages(st.session_state)

conversation_path = Path(__file__).resolve().parent / "data" / "conversation.json"

# TODO 6：增加“保存对话”按钮。空历史只提示，不写文件；
# 非空时调用 save_messages(conversation_path, messages)，成功或失败分别提示。
if st.sidebar.button("保存对话"):
    if not messages:
        st.warning("当前没有对话内容可保存。")
    else:
        try:
            save_messages(conversation_path, messages)
            st.success("对话已保存。")
        except (ValueError, OSError) as e:
            st.error(f"保存对话时出错：{e}")

# TODO 7：增加“加载对话”按钮。文件不存在时提示并保留当前历史；
# 存在时先读取到临时变量，只有成功后才替换会话历史并 st.rerun()。
# 加载失败时展示错误，保留当前历史。
if st.sidebar.button("加载对话"):
    try:
        loaded_messages = load_messages(conversation_path)
        if loaded_messages:
            clear_messages(st.session_state)
            for msg in loaded_messages:
                append_message(st.session_state, msg["role"], msg["content"])
            st.rerun()
        else:
            st.warning("未找到有效的对话文件。")
    except (ConversationFileError, ValueError, OSError) as e:
        st.error(f"加载对话时出错：{e}")
        

# TODO 2：遍历 messages，按 role 展示每条 content。
for message in messages:
    if message["role"] == "user":
        st.chat_message("user").write(message["content"])
    elif message["role"] == "assistant":
        st.chat_message("assistant").write(message["content"])

# TODO 3：使用 st.chat_input() 获取 prompt。
prompt = st.chat_input("请输入您的问题：")

# TODO 4：收到问题时，追加 user 消息并展示，再调用 request_reply()。
# 请求必须包含完整 messages，不能只传当前问题。
if prompt:
    messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    try:
        reply = request_reply(provider, model, messages, timeout=timeout)
    except RuntimeError as e:
        st.error(f"错误：{e}")
    except ValueError as e:
        st.error(f"错误：{e}")
    else:
        messages.append({"role": "assistant", "content": reply})
        st.chat_message("assistant").write(reply)

# TODO 5：捕获 RuntimeError、ValueError 并展示错误；
# 成功时才追加 assistant 消息并展示回答。
