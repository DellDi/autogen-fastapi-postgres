# 快速启动指南

## 环境要求

- Python 3.13+
- PostgreSQL 数据库

## 安装依赖

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

## 配置数据库

1. 创建 PostgreSQL 数据库：

```bash
createdb autogen_db
```

2. 在项目根目录下创建 `.env` 文件，配置数据库连接：

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/autogen_db
```

根据你的 PostgreSQL 配置，修改用户名、密码和数据库名。

## 配置模型

在项目根目录下创建 `model_config.yaml` 文件，配置你的模型设置：

```yaml
class: autogen_core.models.openai.OpenAIChatCompletionClient
config:
  model: gpt-3.5-turbo
  api_key: your_openai_api_key
```

## 运行数据库迁移

```bash
cd /Users/delldi/work-code/aigc-step/autogen-example/agentchat_fastapi
alembic upgrade head
```

如果你看到以下输出，说明迁移成功：

```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 001, 初始迁移
INFO  [alembic.runtime.migration] Running upgrade 001 -> 002, 添加thought字段
```

## 启动应用

有两种方式启动应用：

### 1. 启动API服务

```bash
cd /Users/delldi/work-code/aigc-step/autogen-example/agentchat_fastapi
uv run -m main
```

API服务将在 http://localhost:8001 上运行，提供完整的API功能。

### 2. 启动示例应用

```bash
cd /Users/delldi/work-code/aigc-step/autogen-example/agentchat_fastapi
uv run -m example/app
```

示例应用将在 http://localhost:8001 上运行，提供聊天界面和基本API功能。

## 使用应用

### 使用示例应用

1. 打开浏览器，访问 http://localhost:8001
2. 在聊天界面中输入消息，与智能体进行交互
3. 系统会自动创建会话并保存历史记录

### 使用API

#### 新版API（推荐）

所有新的API端点都以 `/api` 为前缀：

##### 创建新会话

```bash
curl -X POST http://localhost:8001/api/sessions
```

##### 发送消息到特定会话

```bash
curl -X POST http://localhost:8001/api/sessions/{session_id}/chat \
  -H "Content-Type: application/json" \
  -d '{"source": "user", "content": "你好", "type": "TextMessage"}'
```

##### 获取会话历史记录

```bash
curl http://localhost:8001/api/sessions/{session_id}/history
```

#### 旧版API（兼容性）

为了兼容性，保留了原有的API端点：

##### 发送消息（自动使用最新会话）

```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"source": "user", "content": "你好", "type": "TextMessage"}'
```

##### 获取最新会话的历史记录

```bash
curl http://localhost:8001/history
```

## 故障排除

1. 如果遇到数据库连接问题，检查 `.env` 文件中的连接配置是否正确
2. 如果遇到模型调用问题，检查 `model_config.yaml` 文件中的配置是否正确
3. 如果遇到依赖问题，尝试重新安装依赖
4. 如果数据库迁移失败，可以尝试以下步骤：
   - 检查 PostgreSQL 服务是否正常运行
   - 确认数据库用户有足够的权限
   - 查看 alembic 日志，了解具体错误原因
5. 如果API路由不可访问，检查是否使用了正确的URL前缀（新API使用`/api`前缀）
