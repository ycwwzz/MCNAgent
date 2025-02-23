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
st.title("🖼️ 图片识别机器人")

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 用户输入区域
with st.container():
    col1, col2 = st.columns([3, 1])
    with col1:
        image_url = st.text_input(
            "请输入图片URL地址",
            placeholder="例如：https://example.com/image.jpg",
            key="image_input"
        )
    with col2:
        if st.button("开始识别", use_container_width=True):
            if image_url:
                # 添加用户消息到历史
                st.session_state.messages.append({
                    "role": "user",
                    "content": f"![图片]({image_url})"
                })

                # 构建请求数据
                payload = {
                    "inputs": {"url": image_url},
                    "query": "识别图片",
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
                    with st.spinner("正在分析图片..."):
                        response = requests.post(
                            API_URL,
                            headers=headers,
                            data=json.dumps(payload))

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
                st.warning("请输入有效的图片URL地址")

# 实时更新聊天界面
for message in st.session_state.messages[-2:]:  # 仅显示最近两次交互
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(message["content"])  # 显示图片URL
        else:
            st.markdown(f"**识别结果**:\n{message['content']}")