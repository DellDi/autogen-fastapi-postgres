"""
AutoGen v0.5.6 GraphFlow - Parallel Flow with Join 示例

这个示例展示了如何使用AutoGen v0.5.6的GraphFlow功能创建并执行一个包含并行处理和合并节点的工作流。
在这个示例中，我们将创建以下工作流：
1. 一个编写人员(writer)负责起草一个短文段
2. 两个编辑同时工作：一个负责语法(editor_grammar)，一个负责风格(editor_style)
3. 最后一个终审编辑(final_reviewer)将两个编辑的结果进行整合

GraphFlow 是AutoGen v0.5.6新增的一个实验性功能，它允许你通过有向图来控制多个代理之间的工作流程。
"""

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import DiGraphBuilder, GraphFlow
from autogen_ext.models.openai import OpenAIChatCompletionClient

# 🔥AI超元域频道原创视频
# 创建一个OpenAI模型客户端
client = OpenAIChatCompletionClient(model="gpt-4.1-nano")

# 创建写作代理
writer = AssistantAgent(
    name="writer",  # 代理名称
    model_client=client,  # 使用的模型客户端
    system_message="你是一名专业的写作者，请根据用户的要求，起草一个关于指定主题的简短文案。",
)

# 创建语法编辑代理
editor_grammar = AssistantAgent(
    name="editor_grammar",
    model_client=client,
    system_message="你是一名语法专家，负责检查文本的语法错误，并提供修正建议。只关注语法方面，不要改变内容和风格。",
)

# 创建风格编辑代理
editor_style = AssistantAgent(
    name="editor_style",
    model_client=client,
    system_message="你是一名文体风格专家，负责优化文本的表达方式、词语选择和整体风格。不要关注语法问题，专注于让文本更加生动有力。",
)

# 创建终审编辑代理
final_reviewer = AssistantAgent(
    name="final_reviewer",
    model_client=client,
    system_message="你是终审编辑，负责将语法编辑和风格编辑的结果整合，制作最终版本。综合考虑语法正确性和表达效果。",
)

# 构建工作流图
# DiGraphBuilder 是一个流畅的API，用于构建有向图
builder = DiGraphBuilder()

# 添加所有节点
builder.add_node(writer).add_node(editor_grammar).add_node(editor_style).add_node(
    final_reviewer
)

# 添加从writer到两个编辑的边（并行展开）
builder.add_edge(writer, editor_grammar)  # writer完成后，editor_grammar开始工作
builder.add_edge(writer, editor_style)  # writer完成后，editor_style也开始工作

# 添加从两个编辑到终审编辑的边（合并节点）
builder.add_edge(
    editor_grammar, final_reviewer
)  # editor_grammar完成后，结果传递给final_reviewer
builder.add_edge(
    editor_style, final_reviewer
)  # editor_style完成后，结果也传递给final_reviewer

# 构建并验证图
graph = builder.build()

# 创建GraphFlow实例
# participants参数指定参与工作流的所有代理
# graph参数指定工作流的执行图
flow = GraphFlow(
    participants=builder.get_participants(),  # 自动获取图中的所有参与者
    graph=graph,  # 指定执行图
)

# 异步运行工作流
import asyncio


async def main():
    # 运行工作流并获取流式输出
    # run_stream方法会返回一个可以异步迭代的事件流
    stream = flow.run_stream(task="请写一段关于人工智能发展历史的短文。")

    # 显示每个步骤的输出
    async for event in stream:
        # 检查event是否是TaskResult对象（最终结果）
        if hasattr(event, "source"):
            # 如果是消息对象，直接打印source和content
            print(f"========== {event.source} ==========")
            print(event.content)
            print("\n")
        else:
            # 如果是TaskResult对象，打印结果信息
            print("========== 任务完成 ==========")
            print(f"停止原因: {event.stop_reason}")
            print(f"消息数量: {len(event.messages)}")
            print("\n")


# 在脚本中运行时，使用asyncio.run()执行主函数
if __name__ == "__main__":
    asyncio.run(main())

"""
图的执行过程说明：
1. 用户发送任务请求
2. writer代理首先执行，生成初始文段
3. writer完成后，editor_grammar和editor_style同时开始工作（并行执行）
4. 当两个编辑都完成工作后，final_reviewer开始整合他们的修改
5. final_reviewer完成后，工作流结束，返回最终结果

GraphFlow的主要优势:
- 精确控制代理之间的执行顺序
- 支持并行执行多个代理
- 支持条件分支和循环
- 可以过滤每个代理接收的消息，优化上下文管理
"""
