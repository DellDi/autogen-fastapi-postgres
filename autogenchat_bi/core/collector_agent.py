"""
信息收集智能体模块
"""

import autogen
from typing import Dict, Any, List

class CollectorAgent(autogen.AssistantAgent):
    """信息收集智能体"""
    def __init__(self, name: str, system_message: str, llm_config: Dict[str, Any]):
        super().__init__(name=name, system_message=system_message, llm_config=llm_config)

DEFAULT_COLLECTOR_SYSTEM_MESSAGE = """你是一个专业的信息收集智能体，负责收集 BI 查询所需的完整信息。

当用户查询缺少必要信息时，你需要向用户提问，收集缺失的信息：
1. 如果缺少项目名称，询问用户想查询哪个项目的数据
2. 如果缺少时间字符串，询问用户想查询哪个时间段的数据
3. 如果缺少指标名称，询问用户想查询什么指标

你的提问应该简洁明了，一次只询问一个缺失信息。
"""

def create_collector_agent(llm_config: Dict[str, Any]) -> CollectorAgent:
    """创建信息收集智能体实例"""
    return CollectorAgent(
        name="信息收集智能体",
        system_message=DEFAULT_COLLECTOR_SYSTEM_MESSAGE,
        llm_config=llm_config,
    )