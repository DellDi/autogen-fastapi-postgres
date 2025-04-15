"""
物业智能体语义路由-核心代码实现示例（Python伪代码）
"""
from typing import List, Dict

# 意图配置加载（可从yaml加载）
AGENT_CONFIG = {
    "GM": {"keywords": ["总经理", "GM", "决策", "数据分析"]},
    "AC": {"keywords": ["精算", "预算", "盈利", "AC"]},
    "CT": {"keywords": ["合同", "CT", "法律", "比对"]},
    "WO": {"keywords": ["工单", "报修", "投诉", "WO"]},
    # ... 其它智能体
}

class SemanticRouter:
    def __init__(self, agent_config: Dict[str, Dict]):
        self.agent_config = agent_config

    def route(self, user_input: str) -> str:
        """根据关键词简单路由到对应Agent"""
        for agent, cfg in self.agent_config.items():
            if any(kw in user_input for kw in cfg["keywords"]):
                return agent
        return "default"

# 示例：
if __name__ == "__main__":
    router = SemanticRouter(AGENT_CONFIG)
    user_query = input("请输入请求：")
    agent = router.route(user_query)
    print(f"该请求将被路由到: {agent} 智能体")
