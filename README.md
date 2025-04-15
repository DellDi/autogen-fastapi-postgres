# autogen-fastapi-postgres

## 项目简介

`autogen-fastapi-postgres` 是一个基于 FastAPI 的现代智能体（Agent）对话服务后端，集成了 PostgreSQL 数据库，支持多种对话前端（如 Chainlit、Streamlit 等），并采用模块化架构，便于扩展和二次开发。

---

## 主要特性

- 🚀 **FastAPI**：高性能异步 API 框架，支持自动文档和类型校验
- 🗄️ **PostgreSQL**：企业级关系型数据库，数据安全可靠
- 🧩 **多前端适配**：支持 Chainlit、Streamlit 等多种对话前端
- 🦾 **异步文件处理**：aiofiles 加持，I/O 高效
- 🛠️ **现代依赖管理**：基于 pyproject.toml + uv，支持快速安装和跨平台兼容
- 🧬 **模块化设计**：核心功能按包划分，便于维护和扩展
- 📝 **自动化脚本**：集成 Alembic 数据库迁移、环境变量管理等

---

## 目录结构

```plaintext
.
├── agentchat_fastapi/      # FastAPI 主后端服务
├── agentchat_chainlit/     # Chainlit 前端适配
├── agentchat_streamlit/    # Streamlit 前端适配
├── core_semantic_router/   # 语义路由与核心逻辑
├── alembic/                # 数据库迁移脚本
├── pyproject.toml          # 依赖与构建配置
├── requirements.txt        # 自动生成的依赖锁定文件
├── README.md               # 项目说明文档
└── ...                     # 其它辅助文件
```

---

## 快速开始

```bash
# 1. 安装依赖（推荐使用 uv）
uv pip install -e .

# 2. 启动 FastAPI 服务
uv run -m agentchat_fastapi.main

# 3. 浏览器访问
# 默认监听 [http://127.0.0.1](http://127.0.0.1):8000/docs 查看接口文档
```

---

## 依赖环境

- Python >= 3.13
- FastAPI
- SQLAlchemy
- asyncpg, psycopg2-binary
- uvicorn
- streamlit, chainlit（可选前端）
- aiofiles, PyYAML 等

---

## 适用场景

- 智能体对话系统后端
- 多前端适配的 AI 应用
- 快速原型和企业级服务部署
如需详细功能说明、开发规范或贡献指南，欢迎补充完善本文件，或联系维护者！