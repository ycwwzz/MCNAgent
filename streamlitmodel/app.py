import streamlit as st
import requests
import json

# 配置API参数（建议使用环境变量或Streamlit Secrets管理敏感信息）
API_URL = "http://61.182.4.90:8088/v1"
API_KEY = "app-xQ7KpRlkhBoEx63D4LcL3Fan"

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = []

# 设置页面标题
st.title("🤖 编程助手机器人")

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 用户输入区域
with st.container():
    col1, col2 = st.columns([3, 1])
    with col1:
        user_input = st.text_input(
            "请输入编程问题或代码片段",
            placeholder="例如：如何修复Python中的IndexError？",
            key="user_input"
        )
    with col2:
        if st.button("发送", use_container_width=True):
            if user_input:
                # 添加用户消息到历史
                st.session_state.messages.append({
                    "role": "user",
                    "content": user_input
                })

                # 构建请求数据
                payload = {
                    "inputs": {"text": user_input},
                    "query": "编程问题",
                    "response_mode": "blocking",
                    "conversation_id": "",
                    "user": "streamlit_user"
                }

                headers = {
                    'Authorization': f'Bearer {API_KEY}',
                    'Content-Type': 'application/json'
                }

                # 发送请求并处理响应
                try:
                    with st.spinner("正在分析问题..."):
                        response = requests.post(
                            API_URL,
                            headers=headers,
                            data=json.dumps(payload)
                        )
                    if response.status_code == 200:
                        result = response.json().get("answer", "未收到有效响应")
                    else:
                        result = f"请求失败（状态码 {response.status_code}）: {response.text}"

                except requests.exceptions.RequestException as e:
                    result = f"网络连接错误: {str(e)}"

                # 添加AI响应到历史
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result
                })

                # 刷新界面显示最新消息
                st.rerun()
            else:
                st.warning("请输入有效的编程问题或代码片段")

# 实时更新聊天界面
for message in st.session_state.messages[-2:]:  # 仅显示最近两次交互
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(message["content"])  # 显示用户输入
        else:
            st.markdown(f"**助手回复**:\n{message['content']}")  # 显示助手回复