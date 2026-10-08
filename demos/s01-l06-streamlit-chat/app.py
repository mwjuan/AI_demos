from __future__ import annotations

import streamlit as st

from chat_state import append_message, clear_messages, initialize_messages, reset_timeout
from model_chat import OllamaChatError, request_ollama_reply

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

if st.sidebar.button("清空聊天"):
    clear_messages(st.session_state)
    st.rerun()

for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

model = st.sidebar.text_input(
    "Ollama 模型",
    value="qwen3:4b",
    key="model",
)


prompt = st.chat_input("输入你的问题")

if prompt:
    append_message(st.session_state, "user", prompt)

    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        with st.spinner("正在思考…"):
            reply = request_ollama_reply(model, messages, timeout=float(timeout))
    except (OllamaChatError, ValueError) as e:
        st.error(str(e))
    else:
        append_message(st.session_state, "assistant", reply)

        with st.chat_message("assistant"):
            st.markdown(reply)