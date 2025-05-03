"""
意图识别智能体模块
"""

from typing import Dict, Any
from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ModelFamily
from autogen_ext.models.openai import OpenAIChatCompletionClient

class IntentAgent(AssistantAgent):
    """意图识别智能体"""
    def __init__(self, name: str, system_message: str, model_client: Any):
        super().__init__(name=name, system_message=system_message, model_client=model_client)

DEFAULT_INTENT_SYSTEM_MESSAGE = """你是一个专业的意图识别智能体，负责分析用户查询的意图。

你需要判断用户查询是否属于 BI 查询，并识别查询中的关键信息：
1. 项目名称
2. 时间字符串
3. 指标名称

如果信息不完整，你需要指出缺失的信息。

输出格式：
```json
{
    "intent": "bi_query" 或 "other",
    "complete": true 或 false,
    "missing_info": ["项目", "时间", "指标"] 中的一个或多个,
    "precinctName": "项目名称1,项目名称2,...",
    "current_date": "时间字符串",
    "targetName": "指标名称"
}
```
"""

def create_intent_agent(llm_config: Dict[str, Any]) -> IntentAgent:
    """创建意图识别智能体实例"""
    # 创建模型客户端
    model_client = OpenAIChatCompletionClient(
        model=llm_config.get("model", "gpt-4o"),
        api_key=llm_config.get("api_key"),
        base_url=llm_config.get("base_url"),
        temperature=llm_config.get("temperature", 0.0),
        model_info={
            "vision": True,
            "function_calling": True,
            "json_output": True,
            "family": ModelFamily.ANY,
            "structured_output": True,
        },
    )

    return IntentAgent(
        name="intent_agent",
        system_message=DEFAULT_INTENT_SYSTEM_MESSAGE,
        model_client=model_client,
    )