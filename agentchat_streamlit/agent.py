import yaml
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_core.models import ChatCompletionClient
from typing import AsyncGenerator, Optional, Union

class Agent:
    def __init__(self) -> None:
        with open("./model_config.yaml", "r") as f:
            model_config = yaml.safe_load(f)
        # Load the model client from config.
        model_client = ChatCompletionClient.load_component(model_config)
        self.agent = AssistantAgent(
            name="assistant",
            model_client=model_client,
            system_message="You are a helpful AI assistant.",
            model_client_stream=True
        )

    async def chat(self, prompt: str, use_streaming: bool = False) -> Union[str, AsyncGenerator[str, None]]:
        """
        与AI助手聊天
        
        Args:
            prompt: 用户输入的提示
            use_streaming: 是否使用流式输出，默认为False
            
        Returns:
            如果use_streaming为False，返回完整的回复字符串
            如果use_streaming为True，返回一个异步生成器，可以逐步获取回复
        """
        if use_streaming:
            return self.chat_stream(prompt)
        
        # 非流式输出模式
        response = await self.agent.on_messages(
            [TextMessage(content=prompt, source="user")],
            CancellationToken(),
        )
        assert isinstance(response.chat_message, TextMessage)
        return response.chat_message.content
        
    async def chat_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        """流式输出聊天响应"""
        # 创建消息并获取流式响应生成器
        stream_generator = self.agent.on_messages_stream(
            [TextMessage(content=prompt, source="user")],
            CancellationToken(),
        )
        
        # 初始化完整响应
        full_response = ""
        
        # 逐步产生流式响应
        async for chunk in stream_generator:
            if hasattr(chunk, 'content') and chunk.content:
                full_response += chunk.content
                yield chunk.content
        
        # 如果没有获得任何内容，返回一个空字符串
        if not full_response:
            yield ""
