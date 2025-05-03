# AutoGen BI 智能体

基于 AutoGen 框架实现的纯粹 BI 查询智能体，专注于多轮对话、意图识别和信息收集功能。

## 🚀 特性

- **多轮对话**：支持上下文记忆和连续对话，通过唯一会话ID标识
- **意图识别**：快速判断用户查询是否为 BI 相关，非相关查询直接跳过
- **信息收集**：智能收集缺失的项目、时间和指标信息
- **参数提取**：从对话中精准提取关键参数，便于外部 API 调用
- **项目名称提取**：基于命名实体识别和规则匹配，提取不含"项目"字样的最小化项目名称
- **高性能**：查询响应时间控制在 2-3 秒内
- **兼容性**：支持讯飞maas平台的API（OpenAI 接口兼容）

## 📋 目录结构

```
autogenchat_bi/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── bi_orchestrator.py  # BI 智能体编排器 (原 bi_agent.py)
│   ├── collector_agent.py # 信息收集智能体
│   └── intent_agent.py    # 意图识别智能体
├── utils/
│   ├── __init__.py
│   ├── date_parser.py     # 日期解析工具
│   └── project_extractor.py # 项目名称提取工具
├── examples/
│   ├── __init__.py
│   └── run_bi_agent.py    # 使用示例 (原 example.py)
└── README.md              # 项目文档
```

## 💡 核心组件

- **BIOrchestrator**：主智能体，协调整个对话流程（在代码中仍命名为BIAgent）
- **意图识别智能体**：判断查询意图，提取关键参数
- **信息收集智能体**：收集缺失信息，完善查询条件
- **DateParser**：解析各种时间表达，支持相对时间
- **ProjectExtractor**：提取项目名称，基于命名实体识别和规则匹配技术

## 🔧 使用方法

### 基本使用

```python
from autogenchat_bi.core.bi_orchestrator import BIAgent

# 创建 BI 智能体
bi_agent = BIAgent(
    model_config={
        "config_list": [
            {
                "model": "your_model_id",
                "api_key": "your_api_key",
                "base_url": "your_api_base_url",
                "api_type": "openai",
                "extra_body": {"search_disable": False, "show_ref_label": True},
            }
        ],
        "temperature": 0.4,
        "max_tokens": 8192,
    },
    conversation_id="unique_conversation_id"
)

# 处理用户查询
result = bi_agent.process_query("华南物业2024年的物业费收缴率是多少？")

# 获取处理结果
print(f"响应: {result['response']}")
if result["is_complete"] and result["extracted_params"]:
    print(f"提取的参数: {result['extracted_params']}")
    # 提取的项目名称
    if "projects" in result["extracted_params"]:
        print(f"提取的项目: {result['extracted_params']['projects']}")
```

### 单独使用项目名称提取器

```python
from autogenchat_bi.utils.project_extractor import ProjectExtractor

# 初始化项目名称提取器
extractor = ProjectExtractor(
    llm_config={
        "config_list": [
            {
                "model": "your_model_id",
                "api_key": "your_api_key",
                "base_url": "your_api_base_url",
                "api_type": "openai",
            }
        ],
        "temperature": 0.4,
    }
)

# 提取项目名称
text = "华南物业和华中物业的收缴率对比"
projects = extractor.extract_projects(text)
print(f"提取的项目: {projects}")  # 输出: 华南,华中
```

### 完整示例

运行示例程序：

```bash
uv run -m autogenchat_bi.examples.run_bi_agent
```

## 🔧 安装

```bash
# 安装依赖
uv pip install -e .

# 或使用 pip
pip install -e .
```

## 🚀 运行

```bash
# 启动服务
uv run -m autogenchat_bi.main

# 或使用 python
python -m autogenchat_bi.main
```

## 📊 流程图

```mermaid
flowchart TD
    Start[用户查询] --> IntentAgent[意图识别智能体]
    Start --> ProjectExtractor[项目名称提取器]
    ProjectExtractor --> IntentAgent
    IntentAgent --> InfoCheck{信息是否完整?}
    InfoCheck -- 否 --> CollectorAgent[信息收集智能体]
    CollectorAgent --> InfoCheck
    InfoCheck -- 是 --> QueryAgent[数据查询智能体]
    QueryAgent --> FormatAgent[响应格式化智能体]
    FormatAgent --> Response[返回响应]
```

## 📝 配置

创建 `.env` 文件，参考 `.env.example` 进行配置：

```
# API 配置
API_HOST=0.0.0.0
API_PORT=8000

# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/bi_db

# 模型配置
MODEL_API_KEY=your_api_key
MODEL_API_BASE=http://maas-api.cn-huabei-1.xf-yun.com/v1
MODEL_SERVICE_ID=your_service_id
```

## 📄 许可证

MIT
