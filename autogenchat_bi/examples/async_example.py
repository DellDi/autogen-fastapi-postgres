#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
异步 BI 智能体示例
展示如何使用最新版 AutoGen 框架的异步方式调用 BI 智能体
支持流式和非流式模式切换
"""

import os
import asyncio
import json
import argparse
from typing import Dict, Any
from dotenv import load_dotenv
from autogenchat_bi.core.bi_orchestrator import BIAgent

# 解析命令行参数
def parse_args():
    parser = argparse.ArgumentParser(description="异步 BI 智能体示例")
    parser.add_argument(
        "--stream",
        action="store_true",
        default=True,
        help="是否启用流式模式，默认为 True"
    )
    parser.add_argument(
        "--no-stream",
        action="store_false",
        dest="stream",
        help="禁用流式模式"
    )
    parser.add_argument(
        "--print",
        action="store_true",
        default=False,
        help="是否打印流式输出，默认为 False"
    )
    return parser.parse_args()

# 加载环境变量
load_dotenv()


async def main():
    """异步主函数"""
    # 解析命令行参数
    args = parse_args()

    # 打印当前模式设置
    print(f"\n[配置信息] 流式模式: {'启用' if args.stream else '禁用'}, 打印流式输出: {'启用' if args.print else '禁用'}\n")

    # 配置模型参数
    model_config = {
        "model": os.getenv("OPENAI_API_MODEL", "xop3qwen30b"),  # 或其他兼容的模型
        "api_key": os.getenv("OPENAI_API_KEY", ""),
        "base_url": os.getenv(
            "OPENAI_API_BASE_URL", "http://maas-api.cn-huabei-1.xf-yun.com/v1"
        ),  # 本地开发使用的是讯飞maas平台的相关qwen30b模型
        "temperature": 0.3,
        # 百炼 API 需要流式模式，我们需要在 extra_body 中设置
        "extra_body": {
            "stream": True,  # 启用流式模式，支持百炼等只支持流式的模型
        },
        "model_info": {
            "vision": True,
            "function_calling": True,
            "json_output": True,
            "family": ["xop3qwen30b"],
            "structured_output": True,
        },
        # 流式模式配置
        "use_stream_mode": args.stream,  # 是否启用流式模式
        "print_stream_output": args.print,  # 是否打印流式输出
    }

    # 初始化 BI 智能体
    bi_agent = BIAgent(model_config=model_config)

    # 示例查询
    queries = [
        # "华东物业的收缴率是多少？",
        "查一下最近三年的旧欠实收",
    ]

    # 异步处理查询
    for query in queries:
        print(f"\n处理查询: {query}")

        # 使用异步方法处理查询
        result = await bi_agent.process_query_async(query)

        # 打印结果
        print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")

        # 如果需要收集更多信息，模拟用户输入
        if result.get("is_bi_query") and not result.get("is_complete", False):
            missing_info = result.get("missing_info", [])
            print(f"需要收集的信息: {', '.join(missing_info)}")

            # 模拟用户提供缺失信息的响应
            if "项目" in missing_info:
                follow_up = "华东物业"
            elif "时间" in missing_info:
                follow_up = "2024年"
            elif "指标" in missing_info:
                follow_up = "物业费收缴率"
            else:
                follow_up = "我想查看物业费收缴率"

            print(f"用户响应: {follow_up}")

            # 处理后续响应
            follow_up_result = await bi_agent.process_query_async(follow_up)
            print(
                f"后续结果: {json.dumps(follow_up_result, ensure_ascii=False, indent=2)}"
            )


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())
