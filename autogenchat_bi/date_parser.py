"""
日期解析工具模块
提供高级日期字符串解析功能，支持相对时间表达
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class DateParser:
    """日期解析器"""

    def __init__(self, llm_config: Dict[str, Any]):
        """初始化日期解析器

        Args:
            llm_config: 语言模型配置
        """
        self.llm_config = llm_config

        # 导入 AutoGen 组件
        import autogen

        # 创建日期解析智能体
        self.date_agent = autogen.AssistantAgent(
            name="日期解析智能体",
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
            llm_config=self.llm_config,
        )

    def parse_date(
        self, text: str, current_time: Optional[datetime] = None
    ) -> str:
        """解析文本中的日期表达

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

        # 调用日期解析智能体
        response = self.date_agent.generate_reply(
            messages=[{"role": "user", "content": prompt}]
        )

        # 清理响应，确保只返回日期字符串
        response = response.strip()

        # 如果响应为空，返回当前年份
        if not response:
            return current_time.strftime("%Y")

        return response
