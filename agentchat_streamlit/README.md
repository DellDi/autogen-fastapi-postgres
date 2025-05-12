# 基于 Streamlit 的智能体聊天助手

本项目是一个使用 [Streamlit](https://streamlit.io/) 快速搭建的 AI 聊天助手示例，支持多种主流大模型后端，易于扩展和二次开发。

---

## 📦 安装依赖

1. 安装基础依赖：
   ```bash
   pip install streamlit
   ```
2. 如需接入 Azure OpenAI 或其它 OpenAI 兼容模型，安装扩展包：
   ```bash
   pip install "autogen-ext[openai,azure]"
   # 仅用 OpenAI 官方模型可用
   # pip install "autogen-ext[openai]"
   ```

---

## ⚙️ 模型配置

在脚本同级目录下新建 `model_config.yml` 文件，配置你想要使用的大模型。例如，接入 Azure OpenAI 的 `gpt-4o-mini` 可参考：

```yml
provider: autogen_ext.models.openai.AzureOpenAIChatCompletionClient
config:
  azure_deployment: "gpt-4o-mini"
  model: gpt-4o-mini
  api_version: 请填写API版本
  azure_endpoint: 请填写Azure端点
  api_key: 请填写API密钥
```

更多模型配置与接入方法详见 [官方文档](https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/models.html)。

---

## 🚀 启动应用

运行如下命令启动 Streamlit 网页应用：
```bash
# 首先复制 model_config.template.yaml 为 model_config.yaml
cp model_config.template.yaml model_config.yaml
# 然后修改 model_config.yaml 中的配置
streamlit run main.py
```

---

> 本项目适合快速体验与定制基于大模型的智能体聊天界面，欢迎根据需求扩展功能！