#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
直接使用 OpenAI API 调用百炼 API 的示例
绕过 AutoGen 的封装，直接使用 OpenAI API 调用百炼 API，确保流式模式被正确启用
"""

import os
import asyncio
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import AsyncOpenAI

# 加载环境变量
load_dotenv()


async def chat_completion_with_stream(
    client: AsyncOpenAI,
    messages: List[Dict[str, Any]],
    model: str = "xop3qwen30b",
    temperature: float = 0.3,
) -> str:
    """使用流式模式调用 OpenAI API

    Args:
        client: OpenAI 客户端
        messages: 对话消息
        model: 模型名称
        temperature: 温度参数

    Returns:
        str: 完整的响应内容
    """
    # 使用流式模式调用 API
    print("开始流式调用...")
    full_content = ""

    try:
        # 正确的方式是直接调用 create 方法，而不是使用 async with
        stream = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            stream=True,  # 启用流式模式，百炼 API 必须启用
        )

        # 处理流式响应
        async for chunk in stream:
            if hasattr(chunk.choices[0], 'delta') and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_content += content
                print(content, end="", flush=True)

        print("\n\n完整响应:", full_content)
        return full_content
    except Exception as e:
        print(f"调用 API 时出错: {e}")
        return f"错误: {e}"


async def main():
    """主函数"""
    # 创建 OpenAI 客户端
    client = AsyncOpenAI(
        api_key=os.getenv("OPENAI_API_KEY", ""),
        base_url=os.getenv(
            "OPENAI_API_BASE_URL", "http://maas-api.cn-huabei-1.xf-yun.com/v1"
        ),
    )

    # 测试简单的对话
    messages = [
        {"role": "system", "content": "你是一个专业的 BI 助手，可以回答各种 BI 相关问题。"},
        {"role": "user", "content": "查一下最近三年的旧欠实收"},
    ]

    print("发送请求到百炼 API...")
    response = await chat_completion_with_stream(
        client=client,
        messages=messages,
        model=os.getenv("OPENAI_API_MODEL", "xop3qwen30b"),
        temperature=0.3,
    )

    print("\n\n测试完成")


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())
