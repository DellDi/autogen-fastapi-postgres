"""
BI 智能体模块
基于 AutoGen 框架实现 BI 查询智能体
"""

import json
import uuid
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from autogenchat_bi.utils.date_parser import DateParser
from autogenchat_bi.core.intent_agent import create_intent_agent
from autogenchat_bi.core.collector_agent import create_collector_agent

# 导入最新版 AutoGen 组件
from autogen_agentchat.agents import UserProxyAgent


class BIAgent:
    """BI 智能体类

    实现基于 AutoGen 框架的 BI 查询智能体，支持多轮对话、意图识别和信息收集
    """

    def __init__(
        self, model_config: Dict[str, Any], conversation_id: Optional[str] = None
    ):
        """初始化 BI 智能体

        Args:
            model_config: 模型配置，包含 API 密钥、基础 URL 等
            conversation_id: 对话 ID，用于多轮对话
        """
        self.model_config = model_config
        self.conversation_id = conversation_id or str(uuid.uuid4())
        self.conversation_history = []

        # 初始化日期解析器
        self.date_parser = DateParser(llm_config=model_config)

        # 初始化项目名称提取器
        from autogenchat_bi.utils.project_extractor import ProjectExtractor

        self.project_extractor = ProjectExtractor(llm_config=model_config)

        # 初始化智能体
        self._init_agents()

    def _init_agents(self):
        """初始化智能体"""
        # 创建意图识别智能体
        self.intent_agent = create_intent_agent(self.model_config)

        # 创建信息收集智能体
        self.collector_agent = create_collector_agent(self.model_config)

        # 用户代理
        self.user_proxy = UserProxyAgent(
            name="user",
            description="用户",
        )

    async def process_query_async(self, query_text: str) -> Dict[str, Any]:
        """异步处理用户查询

        Args:
            query_text: 用户查询文本

        Returns:
            处理结果
        """
        # 添加用户消息到对话历史
        self.conversation_history.append(
            {
                "role": "user",
                "content": query_text,
                "timestamp": datetime.now().isoformat(),
            }
        )

        # 构建上下文
        context = {
            "conversation_id": self.conversation_id,
            "conversation_history": self.conversation_history,
            "current_time": datetime.now().isoformat(),
        }

        # 1. 意图识别
        intent_result = await self._analyze_intent_async(query_text, context)

        # 2. 项目名称提取（无论意图如何，都尝试提取项目名称）
        projects = await self.project_extractor.extract_projects_async(query_text)
        if projects:
            intent_result["projects"] = projects

        # 如果不是 BI 查询，直接返回
        if intent_result.get("intent") != "bi_query":
            response = "抱歉，我只能回答 BI 相关的问题。"
            self.conversation_history.append(
                {
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            return {
                "response": response,
                "conversation_id": self.conversation_id,
                "is_bi_query": False,
            }

        # 2. 信息收集
        if not intent_result.get("complete", False):
            # 如果信息不完整，收集缺失信息
            collector_result = await self._collect_info_async(
                query_text,
                intent_result.get("missing_info", []),
                {
                    "precinctName": intent_result.get("precinctName"),
                    "current_date": intent_result.get("current_date"),
                    "targetName": intent_result.get("targetName", ""),
                },
            )

            response = collector_result.get("response", "请提供更多信息以完成查询。")
            self.conversation_history.append(
                {
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return {
                "response": response,
                "conversation_id": self.conversation_id,
                "is_bi_query": True,
                "is_complete": False,
                "missing_info": intent_result.get("missing_info", []),
                "collected_info": {
                    "precinctName": intent_result.get("precinctName"),
                    "current_date": intent_result.get("current_date"),
                    "targetName": intent_result.get("targetName", ""),
                },
            }

        # 3. 信息完整，准备调用外部 API
        # 注意：实际的 API 调用由外部实现，这里只返回提取的参数
        extracted_params = {
            "precinctName": intent_result.get("precinctName"),
            "current_date": intent_result.get("current_date"),  # 使用解析后的日期
            "targetName": intent_result.get("targetName", ""),
        }

        # 添加系统消息到对话历史（记录提取的参数）
        self.conversation_history.append(
            {
                "role": "system",
                "content": f"参数提取完成: {json.dumps(extracted_params, ensure_ascii=False)}",
                "timestamp": datetime.now().isoformat(),
            }
        )

        return {
            "conversation_id": self.conversation_id,
            "is_bi_query": True,
            "is_complete": True,
            "extracted_params": extracted_params,
        }

    def process_query(self, query_text: str) -> Dict[str, Any]:
        """同步处理用户查询（兼容旧版接口）

        Args:
            query_text: 用户查询文本

        Returns:
            处理结果
        """
        # 使用事件循环运行异步方法
        return asyncio.run(self.process_query_async(query_text))

    async def _analyze_intent_async(
        self, query_text: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """异步分析用户查询意图

        Args:
            query_text: 用户查询文本
            context: 上下文信息

        Returns:
            意图分析结果
        """
        # 构建提示词
        prompt = f"""请分析以下用户查询的意图：

            查询：{query_text}

            上下文：{json.dumps(context, ensure_ascii=False)}

            请判断这是否是一个指标数据查询，如果是，请提取关键信息。
            """

        # 异步调用意图识别智能体
        result = await self.intent_agent.run(task=prompt)
        # 从 TaskResult 对象中获取最后一次响应内容
        response = result.messages[-1].content
        # 解析响应
        try:
            # 尝试从响应中提取 JSON
            import re

            # 使用正则表达式提取 JSON 字符串
            json_match = re.search(r"```json\s*(.+?)\s*```", response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                intent_result = json.loads(json_str)
            else:
                # 如果没有找到 JSON 格式，尝试直接解析整个响应
                intent_result = json.loads(response)

            # 处理日期信息
            if "current_date" in intent_result and intent_result["current_date"]:
                # 使用日期解析器解析日期字符串
                parsed_date = await self.date_parser.parse_date_async(
                    intent_result["current_date"]
                )
                intent_result["current_date"] = parsed_date

            return intent_result
        except Exception as e:
            # 如果解析失败，返回默认结果
            return {
                "intent": "other",
                "complete": False,
                "missing_info": ["precinctName", "current_date", "targetName"],
            }

    def _analyze_intent(
        self, query_text: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """同步分析用户查询意图（兼容旧版接口）

        Args:
            query_text: 用户查询文本
            context: 上下文信息

        Returns:
            意图分析结果
        """
        return asyncio.run(self._analyze_intent_async(query_text, context))

    async def _collect_info_async(
        self, query_text: str, missing_info: List[str], collected_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """异步收集缺失的信息

        Args:
            query_text: 用户查询文本
            missing_info: 缺失的信息列表
            collected_info: 已收集的信息

        Returns:
            收集结果
        """
        # 构建提示词
        prompt = f"""用户查询：{query_text}

        缺失的信息：{', '.join(missing_info)}

        已收集的信息：{json.dumps(collected_info, ensure_ascii=False)}

        请帮助收集缺失的信息，并生成合适的提问。
        """

        # 异步调用信息收集智能体
        result = await self.collector_agent.run(task=prompt)

        # 从 TaskResult 对象中获取最后一次响应内容
        response = result.messages[-1].content

        return {
            "response": response,
            "missing_info": missing_info,
            "collected_info": collected_info,
        }

    def _collect_info(
        self, query_text: str, missing_info: List[str], collected_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """同步收集缺失的信息（兼容旧版接口）

        Args:
            query_text: 用户查询文本
            missing_info: 缺失的信息列表
            collected_info: 已收集的信息

        Returns:
            收集结果
        """
        return asyncio.run(
            self._collect_info_async(query_text, missing_info, collected_info)
        )

    def update_conversation_history(self, role: str, content: str):
        """更新对话历史

        Args:
            role: 角色（user 或 assistant）
            content: 消息内容
        """
        self.conversation_history.append(
            {"role": role, "content": content, "timestamp": datetime.now().isoformat()}
        )

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """获取对话历史

        Returns:
            对话历史列表
        """
        return self.conversation_history
