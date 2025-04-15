# FastAPI智能体聊天应用

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
├── init_db.py              # 数据库初始化脚本
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
- 自动数据库初始化脚本

## 快速开始

### 环境要求

- Python 3.13+
- PostgreSQL 数据库

### 安装依赖

使用 uv 安装依赖：

```bash
uv pip install -e .
```
### 配置数据库

1. 在项目根目录下创建 `.env` 文件，配置数据库连接：

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

### 初始化数据库

使用初始化脚本自动创建数据库和执行迁移：

```bash
uv run -m agentchat_fastapi.init_db
```

初始化脚本会自动执行以下操作：
1. 检查数据库是否存在，不存在则创建
2. 创建和修复迁移目录结构（如果需要）
3. 初始化迁移（如果没有现有迁移）
4. 执行数据库迁移

### 启动应用

启动API服务：

```bash
uv run -m agentchat_fastapi.main
```

或者启动示例应用：

```bash
uv run -m agentchat_fastapi.example.app
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

## 服务器部署

### 自动初始化

在服务器上部署时，可以使用 `init_db.py` 脚本自动初始化数据库：

```bash
# 使用默认 .env 文件
uv run -m agentchat_fastapi.init_db

# 指定环境变量文件
uv run -m agentchat_fastapi.init_db --env /path/to/.env

# 禁用自动修复功能
uv run -m agentchat_fastapi.init_db --no-fix
```

### 生产环境启动

在生产环境中，建议使用 Gunicorn 或 Uvicorn 启动应用：

```bash
# 使用 Uvicorn
uvicorn agentchat_fastapi.main:app --host 0.0.0.0 --port 8001

# 使用 Gunicorn（多工作进程）
gunicorn agentchat_fastapi.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8001
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

## 数据库迁移

应用使用 Alembic 管理数据库迁移。以下是常用的迁移操作流程：

### 1. 创建新的迁移版本

当模型发生变化时，可以自动生成迁移脚本：

```bash
# 进入项目目录
cd agentchat_fastapi

# 自动生成迁移脚本，--autogenerate 会检测模型变更
alembic revision --autogenerate -m "迁移说明，例如：添加新字段"
```2

这将在 `alembic/versions` 目录下生成一个新的迁移脚本。

### 2. 检查生成的迁移脚本

生成的迁移脚本位于 `alembic/versions` 目录，命名格式为 `{revision_id}_{message}.py`。
**请务必检查生成的脚本**，特别是以下几个方面：

- 表和字段的创建/修改/删除是否符合预期
- 索引的创建/删除是否合理
- 数据类型转换是否正确
- 是否需要添加数据迁移逻辑

### 3. 应用迁移

检查无误后，执行以下命令应用迁移：

```bash
# 升级到最新版本
alembic upgrade head

# 或者升级到特定版本
alembic upgrade {revision_id}
```

### 4. 回滚迁移

如果需要回滚迁移，可以使用：

```bash
# 回滚到上一个版本
alembic downgrade -1

# 回滚到特定版本
alembic downgrade {revision_id}

# 回滚到最初版本
alembic downgrade base
```

### 5. 查看迁移历史和当前版本

```bash
# 查看所有迁移历史
alembic history

# 查看当前数据库版本
alembic current
```

### 6. 给表和字段添加中文注释

在数据库中添加中文注释可以提高可读性和可维护性。在 SQLAlchemy 模型中添加注释的方式：

1. 表级别注释：
```python
class ChatSession(Base):
    __tablename__ = "chat_sessions"
    __table_args__ = {"comment": "聊天会话表"}
    # ...
```

2. 字段级别注释：
```python
name: Mapped[str] = mapped_column(
    String(100), 
    nullable=False, 
    default="新会话",
    comment="会话名称"  # 添加中文注释
)
```

添加注释后，需要创建和应用新的迁移脚本，才能将注释更新到数据库中。

## 更新日志

详见 [CHANGELOG.md](CHANGELOG.md)
