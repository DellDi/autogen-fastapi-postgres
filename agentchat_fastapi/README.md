# 基于FastAPI的智能体聊天应用

基于FastAPI和PostgreSQL的智能体聊天应用，支持会话管理和消息处理。

## 项目结构

```
agentchat_fastapi/
├── alembic/                # 数据库迁移脚本
│   └── versions/           # 迁移版本
│       ├── 001_initial_migration.py
│       └── 002_add_thought_field.py
├── api/                    # API服务
│   ├── __init__.py
│   ├── database.py         # 数据库连接
│   ├── legacy_routes.py    # 旧版兼容路由
│   ├── models.py           # 数据库模型
│   ├── routes.py           # API路由
│   └── services.py         # 服务层
├── docs/                   # 文档
│   ├── api_design.md       # API设计文档
│   ├── architecture.md     # 架构文档
│   ├── data_flow.md        # 数据流程文档
│   ├── database_design.md  # 数据库设计文档
│   ├── index.md            # 文档索引
│   └── quick_start.md      # 快速启动指南
├── example/                # 示例应用
│   ├── __init__.py
│   ├── app.py              # 示例应用入口
│   └── app_agent.html      # 聊天界面
├── .env                    # 环境变量配置
├── alembic.ini             # Alembic配置
├── CHANGELOG.md            # 更新日志
├── main.py                 # 应用主入口
├── model_config_template.yaml  # 模型配置模板
└── README.md               # 项目说明
```

## 功能特性

- 基于FastAPI构建的RESTful API
- PostgreSQL数据库存储会话和消息
- 支持会话管理（创建、获取、列表、删除）
- 支持消息处理（发送、接收、历史记录）
- 智能体状态持久化
- 自动生成会话名称
- 支持思考过程（thought）记录
- 提供示例聊天界面

## 快速开始

### 环境要求

- Python 3.13+
- PostgreSQL 数据库

### 安装依赖

使用 uv 安装依赖：

```bash
cd /Users/delldi/work-code/aigc-step/autogen-example
uv pip install -e .
```

或者使用 pip 安装：

```bash
cd /Users/delldi/work-code/aigc-step/autogen-example
pip install -e .
```

### 配置数据库

1. 创建 PostgreSQL 数据库：

```bash
createdb autogen_db
```

2. 在项目根目录下创建 `.env` 文件，配置数据库连接：

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/autogen_db
```

根据你的 PostgreSQL 配置，修改用户名、密码和数据库名。

### 配置模型

在项目根目录下创建 `model_config.yaml` 文件，配置你的模型设置：

```yaml
class: autogen_core.models.openai.OpenAIChatCompletionClient
config:
  model: gpt-3.5-turbo
  api_key: your_openai_api_key
```

### 运行数据库迁移

```bash
cd /Users/delldi/work-code/aigc-step/autogen-example/agentchat_fastapi
alembic upgrade head
```

### 启动应用

启动API服务：

```bash
cd /Users/delldi/work-code/aigc-step/autogen-example/agentchat_fastapi
python main.py
```

或者启动示例应用：

```bash
cd /Users/delldi/work-code/aigc-step/autogen-example/agentchat_fastapi
python example/app.py
```

应用将在 http://localhost:8001 上运行。

## API使用示例

### API端点

所有新的API端点都以 `/api` 为前缀，例如：

```
/api/sessions
/api/sessions/{session_id}
/api/sessions/{session_id}/chat
/api/sessions/{session_id}/history
```

### 创建新会话

```bash
curl -X POST http://localhost:8001/api/sessions
```

### 发送消息到特定会话

```bash
curl -X POST http://localhost:8001/api/sessions/{session_id}/chat \
  -H "Content-Type: application/json" \
  -d '{"source": "user", "content": "你好", "type": "TextMessage"}'
```

### 获取会话历史记录

```bash
curl http://localhost:8001/api/sessions/{session_id}/history
```

### 旧版API兼容

为了兼容性，保留了原有的API端点：

```
/
/chat
/history
```

## 文档

详细文档位于 `docs/` 目录下：

- [API设计文档](docs/api_design.md)
- [架构文档](docs/architecture.md)
- [数据流程文档](docs/data_flow.md)
- [数据库设计文档](docs/database_design.md)
- [快速启动指南](docs/quick_start.md)

## 数据库架构

```mermaid
erDiagram
    ChatSession ||--o{ ChatMessage : contains
    
    ChatSession {
        uuid id PK
        string name
        datetime created_at
        datetime updated_at
        json agent_state
    }
    
    ChatMessage {
        uuid id PK
        uuid session_id FK
        string source
        text content
        string type
        text thought
        datetime created_at
        json models_usage
        json metadata
    }
```

## 数据流程

```mermaid
sequenceDiagram
    participant User
    participant FastAPI
    participant SessionService
    participant MessageService
    participant Database
    participant Agent
    
    User->>FastAPI: 发送消息
    FastAPI->>SessionService: 获取/创建会话
    SessionService->>Database: 查询/保存会话
    Database-->>SessionService: 返回会话
    FastAPI->>MessageService: 保存用户消息
    MessageService->>Database: 保存消息
    FastAPI->>Agent: 获取智能体并传递消息
    Agent->>Agent: 生成回复和思考过程
    Agent->>FastAPI: 返回回复
    FastAPI->>SessionService: 更新智能体状态
    SessionService->>Database: 保存状态
    FastAPI->>MessageService: 保存智能体回复
    MessageService->>Database: 保存消息
    FastAPI-->>User: 返回智能体回复
```

## 更新日志

详见 [CHANGELOG.md](CHANGELOG.md)
