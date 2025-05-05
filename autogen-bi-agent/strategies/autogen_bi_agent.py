import json
import time
import os
import asyncio
from collections.abc import Generator
from typing import Any, cast, Dict, List, Optional

from dify_plugin.entities.agent import AgentInvokeMessage
from dify_plugin.entities.model.llm import LLMModelConfig, LLMResult, LLMResultChunk
from dify_plugin.entities.model.message import (
    PromptMessageTool,
    UserPromptMessage,
    AssistantPromptMessage,
)
from dify_plugin.entities.tool import ToolInvokeMessage, ToolParameter, ToolProviderType
from dify_plugin.interfaces.agent import AgentModelConfig, AgentStrategy, ToolEntity
from pydantic import BaseModel

# 导入 AutoGen BI 智能体
from autogenchat_bi.core.bi_orchestrator import BIAgent

class AutoGenBIParams(BaseModel):
    maximum_iterations: int
    model: AgentModelConfig
    tools: list[ToolEntity]
    query: str
    conversation_id: Optional[str] = None

class AutoGenBIAgentStrategy(AgentStrategy):
    """AutoGen BI Agent 策略实现"""
    
    def _invoke(self, parameters: dict[str, Any]) -> Generator[AgentInvokeMessage]:
        # 解析参数
        params = AutoGenBIParams(**parameters)
        
        # 创建日志消息
        bi_agent_round_log = self.create_log_message(
            label="AutoGen BI Agent Round",
            data={},
            metadata={},
        )
        yield bi_agent_round_log
        
        # 记录模型调用开始时间
        model_started_at = time.perf_counter()
        model_log = self.create_log_message(
            label=f"{params.model.model} Processing",
            data={},
            metadata={
                "start_at": model_started_at, 
                "provider": params.model.provider
            },
            status=ToolInvokeMessage.LogMessage.LogStatus.START,
            parent=bi_agent_round_log,
        )
        yield model_log
        
        # 构建模型配置
        model_config = {
            "config_list": [
                {
                    "model": params.model.model,
                    "api_key": os.getenv("OPENAI_API_KEY", ""),
                    "base_url": os.getenv("OPENAI_API_BASE_URL", ""),
                    "api_type": "openai",
                    "extra_body": {"search_disable": False, "show_ref_label": True},
                }
            ],
            "temperature": params.model.completion_params.get("temperature", 0.3) if params.model.completion_params else 0.3,
            "max_tokens": params.model.completion_params.get("max_tokens", 8192) if params.model.completion_params else 8192,
            "use_stream_mode": True,
            "print_stream_output": False,
        }
        
        # 获取对话ID
        conversation_id = params.conversation_id or self.session.conversation_id
        
        # 创建 BI 智能体
        bi_agent = None
        result = None
        response = ""
        error_message = ""
        
        try:
            # 创建 BI 智能体
            bi_agent = BIAgent(
                model_config=model_config,
                conversation_id=conversation_id
            )
            
            # 加载历史消息到智能体
            if hasattr(params.model, 'history_prompt_messages') and params.model.history_prompt_messages:
                for message in params.model.history_prompt_messages:
                    if hasattr(message, 'role') and hasattr(message, 'content'):
                        bi_agent.update_conversation_history(
                            role=message.role,
                            content=message.content
                        )
            
            # 处理用户查询 - 使用异步运行但同步等待结果
            event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(event_loop)
            
            result = event_loop.run_until_complete(bi_agent.process_query_async(params.query))
            response = result.get("response", "")
            
        except Exception as e:
            error_message = f"AutoGen BI Agent 执行出错: {str(e)}"
            print(f"Error: {error_message}")
        
        # 完成日志记录
        yield self.finish_log_message(
            log=model_log,
            data={
                "output": response or error_message,
                "is_bi_query": result.get("is_bi_query", False) if result else False,
                "is_complete": result.get("is_complete", False) if result else False,
            },
            metadata={
                "started_at": model_started_at,
                "finished_at": time.perf_counter(),
                "elapsed_time": time.perf_counter() - model_started_at,
                "provider": params.model.provider,
            },
        )
        
        # 如果有错误，返回错误消息
        if error_message:
            yield self.create_text_message(error_message)
            return
        
        # 返回 BI 智能体的响应
        yield self.create_text_message(response)
        
        # 提取参数并设置变量
        variables = {
            "is_bi_query": result.get("is_bi_query", False),
            "is_complete": result.get("is_complete", False),
            "conversation_id": result.get("conversation_id", conversation_id)
        }
        
        # 如果有提取的参数，添加到变量中
        if result.get("extracted_params"):
            extracted_params = result.get("extracted_params", {})
            variables["extracted_params"] = extracted_params
            
            # 提取关键参数并单独存储，方便 Dify 工作流使用
            if "precinctName" in extracted_params:
                variables["project_name"] = extracted_params.get("precinctName")
            if "current_date" in extracted_params:
                variables["date"] = extracted_params.get("current_date")
            if "targetName" in extracted_params:
                variables["target_name"] = extracted_params.get("targetName")
        
        # 设置变量
        for key, value in variables.items():
            self.session.set_variable(key, value)
        
        # 如果信息完整且是 BI 查询，可以在这里添加后续处理逻辑
        if result.get("is_complete", False) and result.get("is_bi_query", False):
            yield self.create_log_message(
                label="BI 参数提取完成",
                data={
                    "extracted_params": result.get("extracted_params", {})
                },
                metadata={},
                parent=bi_agent_round_log,
            )
