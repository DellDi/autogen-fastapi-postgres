# -*- coding: utf-8 -*-
"""
项目名称提取器示例

该示例展示了如何使用ProjectExtractor从文本中提取项目名称。
"""

import os
import sys
import json
from typing import Dict, Any

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autogenchat_bi.utils.project_extractor import ProjectExtractor


def main():
    """运行项目名称提取器示例"""
    # 模型配置（实际使用时需要替换为有效的配置）
    model_config = {
        "config_list": [
            {
                "model": "your_model_id",
                "api_key": "your_api_key",
                "base_url": "your_api_base_url",
                "api_type": "openai",
            }
        ],
        "temperature": 0.3,
    }

    # 初始化项目名称提取器
    extractor = ProjectExtractor(llm_config=model_config)

    # 测试用例
    test_cases = [
        "华南物业的2024年收缴率是多少",
        "华中物业和西南物业的去年12个月的旧欠实收是多少"
        "华中物业和西南物业的去年的旧欠实收是多少",
        "西南物业的全年收入是多少？",
        "北区和东部物业的物业费收入对比",
        "成都高新园区和天府新区的收入情况",
    ]

    # 处理每个测试用例
    for i, text in enumerate(test_cases, 1):
        projects = extractor.extract_projects(text)
        print(f"测试 {i}: {text}")
        print(f"提取的项目: {projects}")
        print("-" * 50)


if __name__ == "__main__":
    main()