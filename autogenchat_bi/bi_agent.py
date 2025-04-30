"""
BI 智能体模块
基于 AutoGen 框架实现 BI 查询智能体
"""

import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from autogenchat_bi.date_parser import DateParser

# 导入 AutoGen 组件
import autogen


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

        # 初始化智能体
        self._init_agents()

    def _init_agents(self):
        """初始化智能体"""
        # 意图识别智能体
        self.intent_agent = autogen.AssistantAgent(
            name="意图识别智能体",
            system_message="""你是一个专业的意图识别智能体，负责分析用户查询的意图。

            你需要判断用户查询是否属于 BI 查询，并识别查询中的关键信息：
            1. 项目名称
            2. 时间范围
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
            """,
            llm_config=self.model_config,
        )

        # 信息收集智能体
        self.collector_agent = autogen.AssistantAgent(
            name="信息收集智能体",
            system_message="""你是一个专业的信息收集智能体，负责收集 BI 查询所需的完整信息。

            当用户查询缺少必要信息时，你需要向用户提问，收集缺失的信息：
            1. 如果缺少项目名称，询问用户想查询哪个项目的数据
            2. 如果缺少时间范围，询问用户想查询哪个时间段的数据
            3. 如果缺少指标名称，询问用户想查询什么指标

            你的提问应该简洁明了，一次只询问一个缺失信息。
            """,
            llm_config=self.model_config,
        )

        # 用户代理
        self.user_proxy = autogen.UserProxyAgent(
            name="用户",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            code_execution_config=False,
        )

    def process_query(self, query_text: str) -> Dict[str, Any]:
        """处理用户查询

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
        intent_result = self._analyze_intent(query_text, context)

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
            collector_result = self._collect_info(
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

    def _analyze_intent(
        self, query_text: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """分析用户查询意图

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

            请判断这是否是一个 BI 查询，并提取关键信息。
            """

        # 调用意图识别智能体
        response = self.intent_agent.generate_reply(
            messages=[{"role": "user", "content": prompt}]
        )

        # 解析响应
        try:
            # 尝试从响应中提取 JSON
            import re

            json_match = re.search(r"```json\n(.*?)\n```", response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                result = json.loads(json_str)
            else:
                # 尝试直接解析整个响应
                result = json.loads(response)

            return result

        except (json.JSONDecodeError, AttributeError):
            # 如果解析失败，返回默认结果
            return {
                "intent": "bi_query",
                "complete": False,
                "missing_info": ["项目", "时间", "指标"],
                "precinctName": None,
                "current_date": None,
                "targetName": "",
            }

    def _collect_info(
        self, query_text: str, missing_info: List[str], collected_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """收集缺失信息

        Args:
            query_text: 用户查询文本
            missing_info: 缺失的信息列表
            collected_info: 已收集的信息

        Returns:
            收集结果
        """
        # 构建提示词
        prompt = f"""用户查询：{query_text}

            缺失信息：{', '.join(missing_info)}

            已收集的信息：{json.dumps(collected_info, ensure_ascii=False)}

            请生成一个简洁明了的问题，向用户收集缺失信息。一次只询问一个信息。
            """

        # 调用信息收集智能体
        response = self.collector_agent.generate_reply(
            messages=[{"role": "user", "content": prompt}]
        )

        return {
            "response": response,
            "missing_info": missing_info,
            "collected_info": collected_info,
        }

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
