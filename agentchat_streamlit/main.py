import asyncio

import streamlit as st
from agent import Agent

async def process_stream(agent, prompt):
    """处理流式响应并在Streamlit界面上显示"""
    # 创建一个空的消息占位符
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # 使用流式API获取响应
        async for chunk in agent.chat_stream(prompt):
            full_response += chunk
            # 添加闪烁的光标来模拟打字效果
            message_placeholder.markdown(full_response + "▌")
        
        # 最终显示完整响应（无光标）
        message_placeholder.markdown(full_response)
    
    # 将完整响应添加到会话状态
    return full_response

async def process_non_stream(agent, prompt):
    """处理非流式响应并在Streamlit界面上显示"""
    with st.chat_message("assistant"):
        with st.spinner("正在生成回复..."):
            # 使用非流式方式获取完整响应
            response = await agent.chat(prompt)
            st.markdown(response)
    
    return response

def main() -> None:
    st.set_page_config(page_title="AI Chat Assistant", page_icon="🤖")
    st.title("AI Chat Assistant 🤖")

    # 侧边栏设置
    with st.sidebar:
        st.title("设置")
        # 流式输出开关
        if "use_streaming" not in st.session_state:
            st.session_state["use_streaming"] = True
        
        use_streaming = st.toggle("流式输出", value=st.session_state["use_streaming"], help="启用流式输出可以看到AI实时生成回复的过程")
        
        # 更新会话状态
        if use_streaming != st.session_state["use_streaming"]:
            st.session_state["use_streaming"] = use_streaming
            st.rerun()

    # adding agent object to session state to persist across sessions
    # stramlit reruns the script on every user interaction
    if "agent" not in st.session_state:
        st.session_state["agent"] = Agent()

    # initialize chat history
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # displying chat history messages
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("请输入您的问题...")
    if prompt:
        # 显示用户输入
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 根据设置选择流式或非流式输出
        if st.session_state["use_streaming"]:
            full_response = asyncio.run(process_stream(st.session_state["agent"], prompt))
        else:
            full_response = asyncio.run(process_non_stream(st.session_state["agent"], prompt))
        
        # 保存响应到会话状态
        st.session_state["messages"].append({"role": "assistant", "content": full_response})


if __name__ == "__main__":
    main()
