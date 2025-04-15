# 基于 AutoGen 与 Chainlit 的多智能体聊天应用

本示例演示如何使用 [AutoGen AgentChat](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/index.html) 与 [Chainlit](https://github.com/Chainlit/chainlit) 快速搭建支持消息流式传输的多智能体聊天界面。

---

## 📦 安装依赖

推荐使用 `pip` 安装所需依赖：

```shell
pip install -U chainlit autogen-agentchat autogen-ext[openai] pyyaml
```

如需使用其他模型服务商，请参考 [模型文档](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/models.html) 并为 `autogen-ext` 安装对应扩展。

---

## ⚙️ 模型配置

请新建 `model_config.yaml` 文件用于自定义模型参数，可参考 `model_config_template.yaml` 模板进行修改。

---

## 🚀 示例运行

### 1. 单智能体对话

与单个 AssistantAgent 聊天：
```shell
chainlit run app_agent.py -h
```
示例提问：`西雅图天气怎么样？`

### 2. 多智能体团队对话

与智能体团队（轮流回复）互动：
```shell
chainlit run app_team.py -h
```
示例提问：`写一首关于冬天的诗。`

团队采用 RoundRobinGroupChat 机制，两位智能体分别负责通用回复与批判反馈，直到“APPROVE”被批判型智能体提及为止。

### 3. 用户代理智能体（UserProxyAgent）

团队中加入用户代理，支持人工审批：
```shell
chainlit run app_team_user_proxy.py -h
```
示例提问：`写一段反转字符串的代码。`

默认情况下，`UserProxyAgent` 会请求用户输入“批准”或“拒绝”，批准后团队停止响应。

---

## 🛠️ 扩展建议

- 尝试更多 [智能体类型](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/agents.html)
- 体验不同 [团队结构](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/teams.html)
- 探索自定义多模态消息的智能体

---

> 如需详细原理与高级用法，请参考：[AutoGen 官方文档](https://microsoft.github.io/autogen/)

