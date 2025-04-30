"""
AutoGen BI 智能体示例
展示如何使用 BI 智能体进行多轮对话和信息收集
"""

import asyncio
import json
import uuid
from typing import Dict, Any, Optional

from autogenchat_bi.bi_agent import BIAgent

# 模型配置
MODEL_CONFIG = {
    "config_list": [
        {
            "model": "xop3qwen30b",  # 例如讯飞星火模型 ID
            "api_key": "sk-FKrDEzhqNVFRSR7o759009732a174222B87cE83cA27aE470",
            "base_url": "http://maas-api.cn-huabei-1.xf-yun.com/v1",
            "api_type": "openai",
            # 移除 extra_headers 中的 lora_id 参数
            "extra_body": {"search_disable": False, "show_ref_label": True, "lora_id": "0"},
        }
    ],
    "temperature": 0.4,
    "max_tokens": 8192,
}

# 对话管理器
CONVERSATIONS = {}

async def process_user_query(
    query_text: str,
    conversation_id: Optional[str] = None
) -> Dict[str, Any]:
    """处理用户查询

    Args:
        query_text: 用户查询文本
        conversation_id: 对话 ID，用于多轮对话

    Returns:
        处理结果
    """
    global CONVERSATIONS

    # 获取或创建 BI 智能体
    if conversation_id and conversation_id in CONVERSATIONS:
        bi_agent = CONVERSATIONS[conversation_id]
    else:
        bi_agent = BIAgent(
            model_config=MODEL_CONFIG,
            conversation_id=conversation_id
        )
        if not conversation_id:
            conversation_id = bi_agent.conversation_id
        CONVERSATIONS[conversation_id] = bi_agent

    # 处理查询
    result =  bi_agent.process_query(query_text)

    # 如果信息完整，调用外部 API
    if result.get("is_bi_query", False) and result.get("is_complete", False):
        # 在实际应用中，这里应该调用外部 API
        # 这里只是示例，打印提取的参数
        print(f"调用外部 API，参数: {json.dumps(result.get('extracted_params', {}), ensure_ascii=False)}")

        # 模拟 API 响应
        api_response = "API 调用成功，数据已返回。"

        # 更新对话历史
        bi_agent.update_conversation_history("assistant", api_response)

        # 更新结果
        result["response"] = api_response

    # 获取对话历史
    conversation_history = bi_agent.get_conversation_history()

    return {
        "conversation_id": conversation_id,
        "response": result.get("response", ""),
        "is_complete": result.get("is_complete", False),
        "extracted_params": result.get("extracted_params", {}) if result.get("is_complete", False) else None,
        "conversation_history": conversation_history
    }

async def main():
    """主函数"""
    print("欢迎使用 BI 智能体！输入 'exit' 退出。")

    conversation_id = str(uuid.uuid4())

    while True:
        # 获取用户输入
        user_input = input("\n用户: ")

        # 检查是否退出
        if user_input.lower() == "exit":
            break

        # 处理用户查询
        result = await process_user_query(user_input, conversation_id)

        # 更新对话 ID
        conversation_id = result["conversation_id"]

        # 打印响应
        print(f"\n智能体: {result['response']}")

        # 对话管理器
        if 'conversation_history' in result:
            print(f"\n对话历史: {json.dumps(result['conversation_history'], ensure_ascii=False)}")

        # 如果信息完整，打印提取的参数
        if result["is_complete"] and result["extracted_params"]:
            print("\n提取的参数:")
            print(f"项目: {result['extracted_params'].get('precinctName', '未提供')}")
            print(f"时间范围: {result['extracted_params'].get('current_date', '未提供')}")
            print(f"指标: {', '.join(result['extracted_params'].get('targetName', ""))}")

if __name__ == "__main__":
    asyncio.run(main())
