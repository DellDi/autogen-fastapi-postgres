"""项目名称提取器模块
提供基于AutoGen的项目名称提取功能，使用大语言模型的语义理解能力
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class ProjectExtractor:
    """项目名称提取器

    从文本中提取项目名称，不包含"项目"字样，遵循最小描述原则。
    使用AutoGen智能体进行语义理解和提取，而非正则表达式。
    """

    def __init__(self, llm_config: Dict[str, Any]):
        """初始化项目名称提取器

        Args:
            llm_config: 语言模型配置，包含API密钥、基础URL等
        """
        self.llm_config = llm_config

        # 导入 AutoGen 组件
        import autogen

        # 创建项目名称提取智能体
        self.project_agent = autogen.AssistantAgent(
            name="项目名称提取智能体",
            system_message="""你是一个专业的项目名称提取专家，负责从文本中识别和提取项目名称。

你的任务是从用户输入的文本中提取出所有项目名称，并遵循以下规则：
1. 提取的项目名称不应包含"项目"字样
2. 遵循最小描述原则，提取最精简的项目名称
3. 能够识别常见的项目命名模式，如：
   - 地域前缀：华东、华南、华西、华北、华中
   - 方位词：东部、南区、西部、北区、中部
   - 城市简称：京、津、沪、渝、蓉、穗、汉等
   - 物业关键词：物业、小区、园区、广场、大厦、中心、花园、公寓等

只返回英文逗号分隔的项目名称列表，不要包含任何其他解释或文本。
如果没有找到项目名称，请返回空字符串。

示例：
- 输入："华东物业的2024年收缴率是多少" -> 华东
- 输入："华中物业和西南物业的去年的旧欠实收是多少" -> 华中,西南
- 输入："成都高新园区和天府新区的收入情况" -> 成都高新,天府新区
""",
            llm_config=self.llm_config,
        )

    def extract_projects(self, text: str) -> str:
        """从文本中提取项目名称

        Args:
            text: 输入文本

        Returns:
            str: 提取的项目名称，多个项目名称用英文逗号分隔
        """
        # 构建提示词
        prompt = f"""请从以下文本中提取项目名称：

文本："{text}"

请只返回英文逗号分隔的项目名称列表，不要包含任何其他解释或文本。
如果没有找到项目名称，请返回空字符串。
"""

        # 调用项目名称提取智能体
        response = self.project_agent.generate_reply(
            messages=[{"role": "user", "content": prompt}]
        )

        # 清理响应，确保只返回项目名称字符串
        response = response.strip()

        return response