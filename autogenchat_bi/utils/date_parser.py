"""日期解析工具模块
提供高级日期字符串解析功能，支持相对时间表达
"""

from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime
import json

# 导入最新版 AutoGen 组件
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient


class DateParser:
    """日期解析器"""

    def __init__(self, llm_config: Dict[str, Any]):
        """初始化日期解析器

        Args:
            llm_config: 语言模型配置，包含模型名称、API密钥等
        """
        # 保存原始配置
        self.llm_config = llm_config
        self.use_stream_mode = llm_config.get("use_stream_mode", True)

        # 创建模型客户端
        model_client = OpenAIChatCompletionClient(
            model=llm_config.get("model", "gpt-4o"),
            api_key=llm_config.get("api_key"),
            base_url=llm_config.get("base_url"),
            temperature=llm_config.get("temperature", 0.0),
            model_info=llm_config.get("model_info"),
        )

        # 创建日期解析智能体
        self.date_agent = AssistantAgent(
            name="date_parser_agent",  # 使用英文名称
            description="日期解析智能体",
            system_message="""你是一个高级语义分析和日期格式化专家，负责识别文本中的日期信息。

你的技能包括识别和计算相对时间表达，并将其转换为 `yyyy` 或 `yyyy-MM` 格式（年或年-月）。

你的目标是准确提取并格式化日期，只返回英文逗号`,`分隔的日期字符串。

示例:
- 文本："华东物业的2024年和2023年物业费收缴率分别是多少，展示为柱状图" -> 2023,2024
- 文本："我们需要上半年的财务报告。" -> 2025-01,2025-02,2025-03,2025-04,2025-05,2025-06
- 文本："会议定于本月20日。" -> 2025-04
- 文本："季度报告应该涵盖上个季度的数据。" -> 2024-10,2024-11,2024-12
- 文本："进五年" -> 2021,2022,2023,2024,2025

只返回日期字符串，不要包含任何其他解释或文本。
""",
            model_client=model_client,
            model_client_stream=self.use_stream_mode,
        )

    async def parse_date_async(
        self, text: str, current_time: Optional[datetime] = None
    ) -> str:
        """异步解析文本中的日期表达

        Args:
            text: 包含日期信息的文本
            current_time: 当前时间，默认为系统当前时间

        Returns:
            格式化的日期字符串，以英文逗号分隔
        """
        # 如果未提供当前时间，使用系统当前时间
        if current_time is None:
            current_time = datetime.now()

        # 构建提示词
        prompt = f"""请从以下文本中提取日期信息并格式化：

文本："{text}"

当前系统时间：{current_time.strftime('%Y-%m-%d %H:%M:%S')}

请只返回英文逗号`,`分隔的日期字符串，不要包含任何其他解释或文本。
"""

        # 检查配置是否启用流式模式
        use_stream_mode = self.llm_config.get("use_stream_mode", True)  # 默认启用流式模式
        print_stream_output = self.llm_config.get("print_stream_output", False)  # 默认不打印

        if use_stream_mode:
            # 使用流式模式
            print("[日期解析] 使用流式模式...")

            # 准备流式输出生成器
            stream_generator = self.date_agent.run_stream(task=prompt)

            # 使用 Console 类处理流式输出并获取结果
            if print_stream_output:
                print("[日期解析] 流式输出开始:")
                result = await Console(stream_generator, output_stats=True)
            else:
                result = await Console(stream_generator, output_stats=False)
        else:
            # 使用非流式模式
            print("[日期解析] 使用非流式模式...")
            result = await self.date_agent.run(task=prompt)

        # 从结果中获取最后一条消息的内容
        response = result.messages[-1].content

        # 清理响应，确保只返回日期字符串
        response = response.strip()

        # 如果响应为空，返回当前年份
        if not response:
            return current_time.strftime("%Y")

        return response

    def parse_date(self, text: str, current_time: Optional[datetime] = None) -> str:
        """同步解析文本中的日期表达（兼容旧版接口）

        Args:
            text: 包含日期信息的文本S
            current_time: 当前时间，默认为系统当前时间

        Returns:
            格式化的日期字符串，以英文逗号分隔
        """
        # 使用事件循环运行异步方法
        return asyncio.run(self.parse_date_async(text, current_time))
