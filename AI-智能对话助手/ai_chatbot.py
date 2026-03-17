import streamlit as st
import os
from openai import OpenAI

# 设置页面配置项
st.set_page_config(
    page_title="你的AI网文书友",
    page_icon="👾",
    layout="wide",
    initial_sidebar_state="expanded",  #侧边栏状态
    menu_items={}
)

# 大标题
st.title("你的AI网文书友")

# OpenAI client
client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com")

# 系统提示词
system_prompt = """
        你叫%s, 现在是一个狂热的中文网络小说爱好者，请完全带入这个角色。
        规则：
            1. 匹配用户的语言
            2. 可以经常性引用网文经典角色台词
            3. 以朋友/书友的方式进行对话
            4. 回复的内容，要充分体现你当前角色的性格特征
        角色性格：
            %s
        你必须严格遵守以上规则来回复用户
        """

# 初始化聊天信息
if "messages" not in st.session_state:
    st.session_state.messages = []

# 初始化昵称
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "小皮"
# 初始化性格
if "character" not in st.session_state:
    st.session_state.character = "中二热血少年"

# 展示聊天信息
for message in st.session_state.messages:
    # 不展示系统提示
    if message["role"] != "system":
        st.chat_message(message["role"]).write(message["content"])

# 左侧侧边栏
with st.sidebar:
    st.subheader("书友信息")
    # 昵称输入框
    nick_name = st.text_input("昵称", placeholder="请输入书友昵称", value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name
    # 性格输入框
    character = st.text_area("性格", placeholder="请输入书友性格", value=st.session_state.character)
    if character:
        st.session_state.character = character


# 聊天消息输入框
prompt = st.chat_input("请输入聊天内容")
if prompt:
    st.chat_message("user").write(prompt)
    print("--------> 调用deepseek大模型，提示词：", prompt)
    # 保存用户输入
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 调用大模型
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt % (st.session_state.nick_name, st.session_state.character)},
            *st.session_state.messages
        ],
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
    print("--------> 大模型返回的结果：", full_response)


    # 保存大模型返回结果
    st.session_state.messages.append({"role": "assistant", "content": full_response})