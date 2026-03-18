import streamlit as st
import os
from openai import OpenAI
from datetime import datetime
import json

# 设置页面配置项
st.set_page_config(
    page_title="你的AI网文书友",
    page_icon="👾",
    layout="wide",
    initial_sidebar_state="expanded",  #侧边栏状态
    menu_items={}
)

# 生成会话标识
def generate_session_id():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# 保存当前会话信息
def save_session():
    if st.session_state.session_id:
        session_data = {
            "nick_name": st.session_state.nick_name,
            "character": st.session_state.character,
            "session_id": st.session_state.session_id,
            "messages": st.session_state.messages
        }

        # 如果 sessions 目录不存在则创建
        if not os.path.exists("sessions"):
            os.mkdir("sessions")

        with open(f"sessions/{st.session_state.session_id}.json", "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

# 加载会话列表
def load_sessions():
    session_list = []
    if os.path.exists("sessions"):
        for filename in os.listdir("sessions"):
            if filename.endswith(".json"):
                session_list.append(filename[:-5])
    session_list.reverse()
    return session_list

# 加载指定会话
def load_session(session_id):
    try:
        if os.path.exists(f"sessions/{session_id}.json"):
            with open(f"sessions/{session_id}.json", "r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.messages = session_data["messages"]
                st.session_state.nick_name = session_data["nick_name"]
                st.session_state.character = session_data["character"]
                st.session_state.session_id = session_data["session_id"]
    except Exception:
        st.error(f"加载会话失败！")

# 删除会话
def delete_session(session_id):
    try:
        if os.path.exists(f"sessions/{session_id}.json"):
            os.remove(f"sessions/{session_id}.json")
            # 如果删除当前会话，则清空会话列表并构建一个新的空会话
            if session_id == st.session_state.session_id:
                st.session_state.messages = []
                st.session_state.session_id = generate_session_id()
    except Exception:
        st.error(f"删除会话失败！")


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
# 会话标识（系统时）
if "session_id" not in st.session_state:
    st.session_state.session_id = generate_session_id()

# 展示聊天信息
st.text(f"会话名称：{st.session_state.session_id}")
for message in st.session_state.messages:
    # 不展示系统提示
    if message["role"] != "system":
        st.chat_message(message["role"]).write(message["content"])

# 左侧侧边栏
with st.sidebar:
    # 会话信息
    st.subheader("AI控制面板")
    # 新建会话按钮
    if st.button("新建会话", width="stretch", icon="👋"):
        # 1.保存当前会话
        save_session()

        # 2.创建新会话
        if st.session_state.messages: # 如果当前会话无内容（还未使用），则不创建新会话
            st.session_state.messages = []
            st.session_state.session_id = generate_session_id()
            save_session()

        # 3.重新运行刷新页面
        st.rerun()

    # 会话历史
    st.text("会话历史")
    session_list = load_sessions()
    for session_id in session_list:
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(session_id, key=f"load_{session_id}", width="stretch", icon="📂", type="primary" if session_id == st.session_state.session_id else "secondary"):
                # 加载会话
                load_session(session_id)
                st.rerun()
        with col2:
            if st.button("", key=f"delete_{session_id}", width="stretch", icon="🗑️"):
                # 删除会话
                delete_session(session_id)
                st.rerun()

    st.divider()  # 分隔线

    # 书友信息
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
    # 保存会话
    save_session()