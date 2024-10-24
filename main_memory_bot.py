import streamlit as st
import json

from langchain.memory import ConversationBufferMemory
from memory_bot import get_chat_response

import os

# 创建页面标题和侧边栏
st.title("💡 个性化记忆问答助手")

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", type="password", placeholder="在此输入您的 OpenAI API Key")
    st.markdown("<span style='color: gray; font-size: 12px;'>不会保存此密钥，您输入的密钥仅在当前会话中可用。</span>", unsafe_allow_html=True)
    openai_api_base = st.text_input("API Base", placeholder="在此输入您的API Base")

    st.markdown("<br><br><br>", unsafe_allow_html=True)  # 使用HTML的换行标签

    # 展示记忆并进行管理
    # 读取 JSON 文件
    def load_json(json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    # 保存更新后的 JSON 文件
    def save_json(data):
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


    # 读取 JSON 数据
    json_file = 'memory.json'
    try:
        data = load_json(json_file)
        # Toggle展开
        if openai_api_key:
            with st.expander("点击展开储存的记忆", expanded=False):
                # 如果储存
                if data.get('facts') and len(data['facts']) > 0:
                    # 展示复选框
                    to_delete = []
                    for i, fact in enumerate(data['facts']):
                        if st.checkbox(fact, key=f"checkbox_{i}"):
                            to_delete.append(fact)

                    # 删除选中的内容
                    if st.button("删除选中的内容"):
                        for fact in to_delete:
                            data['facts'].remove(fact)
                        save_json(data)
                        st.success("已更新记忆！")
                        st.rerun()  # 重新运行脚本以更新界
                else:
                    st.info("还没有记忆被储存，请跟我对话以储存更多记忆。")
    except FileNotFoundError:
        with st.expander("点击展开储存的记忆", expanded=False):
            st.info("还没有记忆被储存，请跟我对话以储存更多记忆。")


# 初始化状态变量
if "memory" not in st.session_state:
    # 初始化用于大模型上下文管理的memory
    st.session_state.memory = ConversationBufferMemory(return_messages=True)
    # 初始化用于储存聊天界面内容的message，messages是一个字典列表，每一个元素都是角色+内容的字典，符合.chat_message()函数的输入格式
    st.session_state.messages = [{"role": "ai", "content": "你好！我是一个能记住你的偏好的助手，随着你跟我的对话增多，我就会更了解你！"}]

# 使用.chat_message()函数，循环渲染历史消息
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

# 创建用户消息输入栏
user_input = st.chat_input()
history = st.session_state.memory.buffer

# 定义用户输入消息后页面的反应
if user_input:
    # 如果未输入API key，提醒用户输入
    if not openai_api_key:
        st.info("请输入你的OpenAI API Key")
        st.stop()

    # 在messages中储存用户输入的prompt，并展示新的输入
    st.session_state.messages.append({"role": "human", "content": user_input})
    st.chat_message("human").write(user_input)

    # 在messages中储存AI的回答，并展示新的输出
    with st.spinner("AI正在思考中，请稍等..."):
        response = get_chat_response(user_input, history, openai_api_key, openai_api_base)
    # 将新对话储存到memory
    st.session_state.memory.save_context(
        {"input": user_input},
        {"output": response}
    )
    # 展示新的输出
    st.session_state.messages.append({"role": "ai", "content": response})
    st.chat_message("ai").write(response)




