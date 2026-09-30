from __future__ import annotations

import streamlit as st

from chat_state import append_message, clear_messages, initialize_messages


st.set_page_config(page_title="个人知识助手", page_icon="📚")
st.title("📚 个人知识助手")

messages = initialize_messages(st.session_state)

if st.sidebar.button("清空聊天"):
    clear_messages(st.session_state)
    st.rerun()

for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("输入你的问题")

if prompt:
    append_message(st.session_state, "user", prompt)
    st.rerun()

# TODO 第七轮：第六轮的 request_ollama_reply() 通过测试后，
# 再在这里接入模型请求、助手回答和 st.error() 错误展示。
