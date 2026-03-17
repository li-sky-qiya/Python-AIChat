import streamlit as st
import os
from openai import OpenAI

# 设置页面配置项
st.set_page_config(
    page_title="AI智能对话小助手",
    page_icon="👾",
    layout="wide",
    initial_sidebar_state="expanded",  #侧边栏状态
    menu_items={}
)

# 大标题
st.title("AI智能对话小助手")

# OpenAI client
client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com")

# 系统提示词
system_prompt = """
你是一个深谙《龙族》全系列的小说粉，请用这个人设进行对话。
"""

# 初始化聊天信息
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt}
    ]

# 展示聊天信息
for message in st.session_state.messages:
    # 不展示系统提示
    if message["role"] != "system":
        st.chat_message(message["role"]).write(message["content"])

# 聊天消息输入框
prompt = st.chat_input("请输入你的问题")
if prompt:
    st.chat_message("user").write(prompt)
    print("--------> 调用deepseek大模型，提示词：", prompt)
    # 保存用户输入
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 调用大模型
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=st.session_state.messages,
        stream=True
    )

    # 非流式输出解析方式
    # print("--------> 大模型返回的结果：", response.choices[0].message.content)
    # st.chat_message("assistant").write(response.choices[0].message.content)

    # 流式输出解析方式
    response_message = st.empty() # 创建一个空消息， 用于保存大模型返回结果
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_response += content
            response_message.chat_message("assistant").write(full_response)


    # 保存大模型返回结果
    st.session_state.messages.append({"role": "assistant", "content": full_response})