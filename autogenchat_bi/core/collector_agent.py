"""
信息收集智能体模块
"""

from typing import Dict, Any, List
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient


class CollectorAgent(AssistantAgent):
    """信息收集智能体"""

    def __init__(self, name: str, description: str, system_message: str, model_client: Any, model_client_stream: bool = False):
        super().__init__(
            name=name, description=description, system_message=system_message, model_client=model_client, model_client_stream=model_client_stream
        )


DEFAULT_COLLECTOR_SYSTEM_MESSAGE = """你是一个专业的信息收集智能体，负责收集 BI 查询所需的完整信息。

当用户查询缺少必要信息时，你需要向用户提问，收集缺失的信息：
1. 如果缺少项目名称，询问用户想查询哪个项目的数据
2. 如果缺少时间字符串，询问用户想查询哪个时间段的数据
3. 如果缺少指标名称，询问用户想查询什么指标

你的提问应该简洁明了，对于缺失的信息可以询问多个。

"""


def create_collector_agent(llm_config: Dict[str, Any], use_stream_mode: bool = False) -> CollectorAgent:
    """创建信息收集智能体实例"""
    # 创建模型客户端
    # 百炼 API 需要流式模式，但我们不能直接设置 stream=True
    # 我们需要在 create 方法调用时设置流式模式
    model_client = OpenAIChatCompletionClient(
        model=llm_config.get("model", "gpt-4o"),
        api_key=llm_config.get("api_key"),
        base_url=llm_config.get("base_url"),
        temperature=llm_config.get("temperature", 0.0),
        model_info=llm_config.get("model_info"),
    )

    return CollectorAgent(
        name="collector_agent",
        description="信息收集智能体",
        system_message=DEFAULT_COLLECTOR_SYSTEM_MESSAGE,
        model_client=model_client,
        model_client_stream=use_stream_mode,
    )
