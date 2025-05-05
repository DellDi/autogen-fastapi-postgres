#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
标准指标名称解析器示例
展示如何使用ChromaDB向量库和标准指标名称解析器
"""

import os
import asyncio
from dotenv import load_dotenv
from autogenchat_bi.utils.target_extractor import TargetExtractor

# 加载环境变量
load_dotenv()

async def main():
    """异步主函数"""
    # 配置模型参数
    model_config = {
        "model": os.getenv("OPENAI_API_MODEL", "xop3qwen30b"),  # 或其他兼容的模型
        "api_key": os.getenv("OPENAI_API_KEY", ""),
        "base_url": os.getenv(
            "OPENAI_API_BASE_URL", "http://maas-api.cn-huabei-1.xf-yun.com/v1"
        ),  # 如果使用讯飞星火等兼容接口，需要设置
        "temperature": 0.2,
        "model_info": {
            "vision": True,
            "function_calling": True,
            "json_output": True,
            "family": ["xop3qwen30b"],
            "structured_output": True,
        },
    }

    # 文档目录和数据库路径
    docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "target-docs")
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")

    # 初始化标准指标名称解析器
    target_extractor = TargetExtractor(
        llm_config=model_config,
        docs_dir=docs_dir,
        db_path=db_path
    )

    # 示例查询
    queries = [
        "物业费收缴率",
        "收缴率",
        "物业收入",
        "利润率",
        "成本率"
    ]

    # 异步处理查询
    for query in queries:
        print(f"\n处理查询: {query}")

        # 使用异步方法提取标准指标名称
        result = await target_extractor.extract_target_async(query)

        # 打印结果
        print(f"标准指标名称: {result}")

if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())
