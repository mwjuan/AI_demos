from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

from chat_state import append_message, clear_messages, initialize_messages, reset_timeout
from model_chat import OllamaChatError, request_ollama_reply

# 将第三课目录加入模块搜索路径，复用已经完成的文件读写逻辑。
store_dir = Path(__file__).resolve().parents[1] / "s01-l03-files-errors"
sys.path.insert(0, str(store_dir))

from conversation_store import (
    ConversationFileError,
    load_messages,
    save_messages,
)

from model_chat import OllamaChatError, request_reply

st.set_page_config(page_title="个人知识助手", page_icon="📚")
st.title("📚 个人知识助手")

if st.sidebar.button("恢复默认超时"):
    reset_timeout(st.session_state)
    
timeout = st.sidebar.number_input(
    "请求超时（秒）",
    min_value=1,
    max_value=600,
    value=120,
    step=10,
    key="timeout",
)

messages = initialize_messages(st.session_state)
path = Path(__file__).resolve().parent / "data" / "conversation.json"

if st.sidebar.button("加载对话"):
    if not path.exists():
        st.warning("还没有保存的对话")
    else:
        try:
            loaded_messages = load_messages(path)
        except (ConversationFileError, ValueError, OSError) as e:
            st.error(f"加载失败：{e}")
        else:
            st.session_state["messages"] = loaded_messages
            st.rerun()

if st.sidebar.button("保存对话"):
    messages = st.session_state["messages"]
    if messages in (None, []):
        st.warning("还没有可保存的对话")
    else:    
        try:
            save_messages(path, messages)
        except (ValueError, OSError) as e:
            st.error(f"保存失败：{e}")
        else:
            st.success("对话已保存")

if st.sidebar.button("清空聊天"):
    clear_messages(st.session_state)
    st.rerun()

for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

provider = st.sidebar.selectbox(
    "模型来源",
    ["ollama", "cloud"],
    key="provider",
)

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

prompt = st.chat_input("输入你的问题")

if prompt:
    append_message(st.session_state, "user", prompt)

    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        with st.spinner("正在思考…"):
            reply = request_reply(provider, model=model, messages=messages, timeout=float(timeout))
    except (RuntimeError, ValueError) as e:
        st.error(str(e))
    else:
        append_message(st.session_state, "assistant", reply)

        with st.chat_message("assistant"):
            st.markdown(reply)
