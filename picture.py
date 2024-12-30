import streamlit as st
from openai import OpenAI

# 设置页面配置
st.set_page_config(
    page_title="心理诊疗助手",
    page_icon="🌟",  # 使用支持的字符或字体图标服务。
    layout="wide",
)

# 应用标题
st.title("心理诊疗助手")

# 设置背景颜色和其他样式
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f0f8ff; /* 背景颜色：浅蓝色 */
        position: relative;
        min-height: 100vh;
    }
    .chat-container {
        max-width: 60%;
        margin: auto;
        position: relative;
        top: 50%;
        transform: translateY(-50%);
    }
    .message {
        border: 1px solid #b3e0ff;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
        background-color: #e6f7ff;
    }
    .user-message {
        text-align: right;
    }
    .input-container {
        display: flex;
        position: fixed;
        bottom: 0;
        width: 100%;
        background-color: #fff;
        padding: 10px;
        box-shadow: 0 -2px 5px rgba(0,0,0,0.1);
    }
    .input-container input {
        flex: 1;
        padding: 10px;
        border: none;
        border-radius: 20px 0 0 20px; /* 圆角仅应用于左边 */
        margin-right: -4px; /* 减少边距使得按钮和输入框紧密相连 */
        background-color: #f0f8ff;
        color: #333;
    }
    .input-container button {
        padding: 10px 20px;
        border: none;
        border-radius: 0 20px 20px 0; /* 圆角仅应用于右边 */
        background-color: #ff4d4d;
        color: white;
        cursor: pointer;
    }
    .input-container button:hover {
        background-color: #e63939;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 使用JavaScript默认收起侧边栏
st.markdown(
    """
    <script>
    document.addEventListener("DOMContentLoaded", function() {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            sidebar.style.display = 'none';
        }
        const sidebarButton = document.querySelector('.sidebar-toggle');
        if (sidebarButton) {
            sidebarButton.addEventListener('click', function() {
                if (sidebar.style.display === 'none') {
                    sidebar.style.display = 'block';
                } else {
                    sidebar.style.display = 'none';
                }
            });
        }
    });
    </script>
    """,
    unsafe_allow_html=True
)

# 初始化会话管理
if "sessions" not in st.session_state:
    st.session_state.sessions = [ [] ]  # 创建一个空的默认会话

if "current_session" not in st.session_state:
    st.session_state.current_session = st.session_state.sessions[0]

# 侧边栏：会话管理
st.sidebar.header("会话管理")

# 使用expander默认收起会话列表
with st.sidebar.expander("会话列表", expanded=False):
    session_list = st.selectbox("选择会话", options=range(len(st.session_state.sessions)),
                                format_func=lambda x: f"会话 {x + 1}")
    if session_list is not None:
        st.session_state.current_session = st.session_state.sessions[session_list]

    # 删除会话
    if st.button("删除当前会话"):
        if st.session_state.current_session in st.session_state.sessions:
            st.session_state.sessions.remove(st.session_state.current_session)
            if st.session_state.sessions:
                st.session_state.current_session = st.session_state.sessions[-1]
            else:
                st.session_state.current_session = []

# 创建新会话按钮保持在侧边栏中
if st.sidebar.button("新建会话"):
    new_session = []
    st.session_state.sessions.append(new_session)
    st.session_state.current_session = new_session

# 显示聊天记录
if st.session_state.current_session is not None:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for message in st.session_state.current_session:
        role = message["role"]
        content = message["content"]
        align = "user-message" if role == "user" else ""
        st.markdown(
            f'<div class="message {align}"><strong>{role.capitalize()}: </strong>{content}</div>',
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # 用户输入区域和发送按钮
    with st.container():
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        col1, col2 = st.columns([10, 1])  # 创建两列，比例为10:1，确保按钮宽度较小
        with col1:
            user_input = st.text_input("请输入您的问题或感受:", key="user_input", label_visibility="hidden")
        with col2:
            send_button = st.button(">", key="send_button")

        st.markdown('</div>', unsafe_allow_html=True)

        # 处理发送按钮点击事件
        if send_button and user_input.strip():
            # 将用户消息添加到当前会话
            st.session_state.current_session.append({"role": "user", "content": user_input})

            # 调用API获取回复
            try:
                client = OpenAI(
                    api_key="sk-0d692a5a1c54424091023205d1bc5ac3",  # 请替换为实际的API密钥
                    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                )
                messages = st.session_state.current_session.copy()
                # 确保第一个消息是system角色
                if messages[0]["role"] != "system":
                    messages.insert(0, {"role": "system", "content": "您是一位心理诊疗助手，专注于提供情感支持和建议。"})

                response = client.chat.completions.create(
                    model="qwen-plus",
                    messages=messages
                )
                assistant_response = response.choices[0].message.content
                st.session_state.current_session.append({"role": "assistant", "content": assistant_response})

                # 刷新页面以显示新消息
                st.rerun()
            except Exception as e:
                st.error(f"发生错误: {e}")
                st.error("请检查API配置并重试。")
else:
    st.write("请创建或选择一个会话开始聊天。")