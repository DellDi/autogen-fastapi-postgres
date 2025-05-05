from dify_plugin.plugin import Plugin
from strategies.autogen_bi_agent import AutoGenBIAgentStrategy

# 创建插件实例
plugin = Plugin()

# 注册策略
plugin.register_agent_strategy("autogen_bi_agent", AutoGenBIAgentStrategy())

# 启动插件
if __name__ == "__main__":
    plugin.run()
