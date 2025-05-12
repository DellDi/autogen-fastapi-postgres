from autogen_agentchat.agents import (
    AssistantAgent,
    MessageFilterAgent,
    MessageFilterConfig,
    PerSourceFilter,
)
from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
import asyncio

# 创建模型客户端
model_client = OpenAIChatCompletionClient(model="gpt-4.1-nano")

# 定义各个专业智能体
# 规划师智能体 - 负责初步旅行计划制定
planner_agent = AssistantAgent(
    "planner_agent",
    model_client=model_client,
    description="一个能够规划旅行的助手。",
    system_message="你是一个帮助用户根据其需求规划旅行计划的助手。提供详细的行程安排、景点建议和时间规划。你的工作是创建基础旅行框架。",
)

# 当地专家智能体 - 提供当地活动和景点建议
local_agent = AssistantAgent(
    "local_agent",
    model_client=model_client,
    description="一个能够推荐当地活动或景点的助手。",
    system_message="你是一个能够为用户推荐真实有趣的当地活动或景点的助手。基于规划师提供的基础框架，补充更多当地特色体验、美食和文化活动的详细信息。注重提供当地特色和独特体验。",
)

# 语言专家智能体 - 提供语言和沟通技巧
language_agent = AssistantAgent(
    "language_agent",
    model_client=model_client,
    description="一个能够为特定目的地提供语言技巧的助手。",
    system_message="你是一个能够提供目的地语言和沟通技巧的助手。基于规划师提供的基础框架，添加有关当地语言、常用短语、沟通礼仪和文化差异的建议，帮助旅行者更好地与当地人交流。",
)

# 总结智能体 - 整合各方建议并生成最终计划
travel_summary_agent = AssistantAgent(
    "travel_summary_agent",
    model_client=model_client,
    description="一个能够总结旅行计划的助手。",
    system_message="""你是一个专门整合最终旅行计划的助手。你的任务是：
1. 查看规划师提供的基础行程框架
2. 融合当地专家提供的特色活动和体验建议
3. 纳入语言专家的语言和沟通技巧

你必须创建一个全面而连贯的最终旅行计划，包括：
- 每日行程安排，包含时间、地点和活动
- 特色体验和美食推荐
- 必要的语言和沟通技巧
- 实用的旅行建议

你的输出格式应为：
- 开头：简短介绍
- 中间：按天详细行程（第一天、第二天、第三天）
- 结尾：旅行贴士，包含语言沟通建议

请确保最终计划综合了所有其他智能体的建议，并且格式清晰、内容完整。
当计划完成，在最后一行单独添加'TERMINATE'作为标记。""",
)

# 使用MessageFilterAgent对每个智能体进行包装以控制消息流
# 当地专家只看到用户请求和规划师的最后一条消息
filtered_local_agent = MessageFilterAgent(
    name="local_agent",
    wrapped_agent=local_agent,
    filter=MessageFilterConfig(
        per_source=[
            PerSourceFilter(source="user", position="first", count=1),
            PerSourceFilter(source="planner_agent", position="last", count=1),
        ]
    ),
)

# 语言专家只看到用户请求和规划师的最后一条消息
filtered_language_agent = MessageFilterAgent(
    name="language_agent",
    wrapped_agent=language_agent,
    filter=MessageFilterConfig(
        per_source=[
            PerSourceFilter(source="user", position="first", count=1),
            PerSourceFilter(source="planner_agent", position="last", count=1),
        ]
    ),
)

# 总结智能体需要看到用户的第一条消息、规划师的最后一条消息、当地专家的最后一条消息和语言专家的最后一条消息
# 这里使用明确的名称并确保配置正确
filtered_summary_agent = MessageFilterAgent(
    name="travel_summary_agent",
    wrapped_agent=travel_summary_agent,
    filter=MessageFilterConfig(
        per_source=[
            PerSourceFilter(source="user", position="first", count=1),
            PerSourceFilter(source="planner_agent", position="last", count=1),
            PerSourceFilter(source="local_agent", position="last", count=1),
            PerSourceFilter(source="language_agent", position="last", count=1),
        ],
        default="exclude",  # 明确默认排除其他消息
    ),
)

# 使用DiGraphBuilder构建混合工作流图
builder = DiGraphBuilder()

# 添加所有节点
builder.add_node(planner_agent).add_node(filtered_local_agent).add_node(
    filtered_language_agent
).add_node(filtered_summary_agent)

# 构建执行流程
# 1. 用户请求首先传递给规划师创建基础框架
# 2. 规划师完成后，同时传递给当地专家和语言专家（并行处理）
# 3. 当地专家和语言专家都完成后，各自的结果传递给总结智能体
# 这创建了一个混合顺序+并行的工作流
builder.add_edge(planner_agent, filtered_local_agent)
builder.add_edge(planner_agent, filtered_language_agent)
builder.add_edge(filtered_local_agent, filtered_summary_agent)
builder.add_edge(filtered_language_agent, filtered_summary_agent)

# 构建并验证图
graph = builder.build()

# 创建GraphFlow团队
flow = GraphFlow(
    participants=builder.get_participants(),
    graph=graph,
)


# 运行工作流并格式化输出
async def main():
    # 运行工作流并以友好格式在控制台显示结果
    await Console(flow.run_stream(task="为我规划一个3天的尼泊尔之旅。"))

    # 关闭模型客户端
    await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())
