# FastAPI 智能体聊天应用文档

## 简介

FastAPI 智能体聊天应用是一个基于 FastAPI 和 AutoGen 框架构建的智能对话系统，使用 PostgreSQL 数据库进行数据存储。本应用支持多会话管理、消息历史记录和智能体状态持久化。

## 文档目录

1. [系统架构](./architecture.md) - 系统整体架构设计和组件说明
2. [数据库设计](./database_design.md) - 数据库模型和关系设计
3. [API 设计](./api_design.md) - API 接口设计和使用说明
4. [数据流程](./data_flow.md) - 系统数据流程和处理逻辑
5. [快速启动指南](./quick_start.md) - 安装、配置和启动应用的步骤

## 核心功能

- **多会话管理**：支持创建和管理多个聊天会话
- **消息历史记录**：保存完整的对话历史记录
- **智能体状态持久化**：在多次交互之间保持智能体状态
- **兼容旧API**：保留原有API以保持兼容性

## 技术栈

- **Web框架**：FastAPI
- **ORM**：SQLAlchemy 2.0
- **数据库**：PostgreSQL
- **迁移工具**：Alembic
- **异步支持**：asyncpg, async/await
- **智能体框架**：AutoGen
- **大语言模型**：支持多种LLM模型

## 版本历史

详细的版本历史请查看 [CHANGELOG.md](../CHANGELOG.md)。

## 贡献指南

欢迎提交问题报告和功能请求。如果您想贡献代码，请遵循以下步骤：

1. Fork 仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个 Pull Request
