# AutoGen BI Agent 插件

## 项目简介

AutoGen BI Agent 是一个基于 AutoGen 框架的 BI 查询智能体，封装为 Dify 的 Agent 策略插件。该插件专注于多轮对话、意图识别和信息收集功能，能够从用户查询中提取项目、时间和指标等关键参数。

## 主要功能

- **多轮对话**：支持上下文记忆和连续对话
- **意图识别**：快速判断用户查询是否为 BI 相关
- **信息收集**：智能收集缺失的项目、时间和指标信息
- **参数提取**：从对话中精准提取关键参数
- **流式模式**：支持流式输出，兼容百炼 API 等只支持流式模式的服务

## 安装步骤

### 开发调试

1. 克隆本仓库或下载插件包
2. 确保已安装所需依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 安装 Dify 插件开发工具：
   ```bash
   pip install dify-plugin-cli
   ```
4. 复制 `.env.example` 并重命名为 `.env`，填入调试信息：
   ```
   INSTALL_METHOD=remote
   REMOTE_INSTALL_HOST=remote
   REMOTE_INSTALL_PORT=5003
   REMOTE_INSTALL_KEY=从 Dify 获取的调试Key
   ```
5. 启动插件进行调试：
   ```bash
   python -m main
   ```

### 打包安装

1. 使用 Dify 官方工具打包插件：
   ```bash
   dify plugin package ./autogen-bi-agent/
   ```
2. 打包后会生成一个 `.difypkg` 格式的插件包文件
3. 在 Dify 管理界面上传生成的 `.difypkg` 文件

## 配置说明

插件支持以下配置项：

- **model**：用于 BI 智能体的模型
- **query**：用户输入的查询文本
- **conversation_id**：对话 ID，用于多轮对话记忆
- **maximum_iterations**：最大迭代次数，默认为 5

## 环境变量

插件需要以下环境变量：

- `OPENAI_API_KEY`：OpenAI API 密钥
- `OPENAI_API_BASE_URL`：（可选）自定义 API 基础 URL，用于兼容服务如百炼 API

## 使用示例

在 Dify 工作流中：

1. 添加 Agent 策略节点，选择 "AutoGen BI Agent"
2. 配置必要参数：
   - 模型：选择合适的模型
   - 用户输入：设置为用户消息
   - 对话 ID：设置为唯一标识符
3. 处理返回结果：
   - 响应内容：智能体的回复
   - 变量：
     - `is_bi_query`：是否为 BI 查询
     - `is_complete`：信息是否完整
     - `extracted_params`：提取的参数
     - `project_name`：提取的项目名称
     - `date`：提取的日期
     - `target_name`：提取的指标名称

## 文件结构

```
autogen-bi-agent/
├── GUIDE.md               # 用户指南
├── README.md              # 项目说明
├── _assets/               # 资源目录
│   └── icon.svg           # 插件图标
├── main.py                # 主入口文件
├── manifest.yaml          # 插件基本配置
├── provider/              # 提供者配置
│   └── autogen_bi_agent.yaml  # Agent 提供者配置
├── requirements.txt       # 依赖项
└── strategies/            # 策略实现
    ├── autogen_bi_agent.py    # BI Agent 策略实现
    └── autogen_bi_agent.yaml  # BI Agent 策略配置
```

## 开发说明

本插件基于现有的 AutoGen BI 智能体代码，通过封装为 Dify 插件接口实现集成，不对原有代码进行修改。

## 许可证

MIT
