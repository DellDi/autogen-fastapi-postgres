# AutoGen GraphFlow 流程思维导图

## 1. GraphFlow 核心架构

```mermaid
graph TD
    subgraph "GraphFlow核心组件"
        A[DiGraphBuilder] -->|构建| B[有向图]
        B -->|验证| C[GraphFlow团队]
        D[MessageFilterAgent] -->|过滤消息| C
        C -->|执行| E[run/run_stream]
        E -->|返回| F[结果/事件流]
    end
    
    subgraph "工作流模式"
        G[顺序执行] 
        H[并行执行]
        I[混合执行]
    end
    
    C --> G
    C --> H
    C --> I
```

## 2. 顺序工作流 (sequential-flow.py)

```mermaid
graph LR
    subgraph "顺序工作流"
        A[用户请求] -->|翻译任务| B[翻译器<br>translator]
        B -->|翻译结果| C[校对者<br>proofreader]
        C -->|校对结果| D[格式化器<br>formatter]
        D -->|最终结果| E[用户]
    end
    
    subgraph "模型后端"
        M1[Ollama<br>qwen3:14b]
        M2[Gemini<br>gemini-2.0-flash-lite]
        M3[OpenAI<br>gpt-4.1-nano]
    end
    
    B -.->|使用| M1
    C -.->|使用| M2
    D -.->|使用| M3
```

## 3. 并行工作流 (parallel-flow.py)

```mermaid
graph TD
    subgraph "并行工作流"
        A[用户请求] -->|写作任务| B[写作者<br>writer]
        B -->|初稿| C[语法编辑<br>editor_grammar]
        B -->|初稿| D[风格编辑<br>editor_style]
        C -->|语法修正| E[终审编辑<br>final_reviewer]
        D -->|风格优化| E
        E -->|最终结果| F[用户]
    end
    
    subgraph "关键特性"
        G["扇出(Fan-out)"]
        H["扇入(Fan-in)"]
        I["并行处理"]
    end
    
    B --> G
    E --> H
    G --> I
```

## 4. 旅行规划团队 (travel-agent.py)

```mermaid
graph TD
    subgraph "旅行规划团队"
        A[用户请求] -->|旅行规划任务| B[规划师<br>planner_agent]
        B -->|基础框架| C[当地专家<br>local_agent]
        B -->|基础框架| D[语言专家<br>language_agent]
        C -->|当地建议| E[总结智能体<br>travel_summary_agent]
        D -->|语言建议| E
        E -->|最终旅行计划| F[用户]
    end
    
    subgraph "消息过滤配置"
        G[规划师<br>全部消息]
        H[当地专家<br>用户首条+规划师末条]
        I[语言专家<br>用户首条+规划师末条]
        J[总结智能体<br>用户首条+各专家末条]
    end
    
    B -.->|接收| G
    C -.->|接收| H
    D -.->|接收| I
    E -.->|接收| J
```

## 5. GraphFlow 与传统群聊对比

```mermaid
graph LR
    subgraph "传统GroupChat"
        A1[智能体A] <-->|全部消息| B1[智能体B]
        B1 <-->|全部消息| C1[智能体C]
        C1 <-->|全部消息| D1[智能体D]
        A1 <-->|全部消息| C1
        A1 <-->|全部消息| D1
        B1 <-->|全部消息| D1
    end
    
    subgraph "GraphFlow"
        A2[智能体A] -->|选择性消息| B2[智能体B]
        A2 -->|选择性消息| C2[智能体C]
        B2 -->|选择性消息| D2[智能体D]
        C2 -->|选择性消息| D2
    end
```

## 6. GraphFlow 应用场景

```mermaid
mindmap
  root((GraphFlow<br>应用场景))
    内容创作
      写作
      编辑
      审核
      发布
    多语言翻译
      翻译
      校对
      本地化
      文化适应
    旅行规划
      行程制定
      当地体验
      语言准备
      综合建议
    产品设计
      需求分析
      概念设计
      原型开发
      用户测试
    研究分析
      数据收集
      数据处理
      结果分析
      报告生成
    教育内容
      课程设计
      内容创建
      教学评估
      学习反馈
```

## 7. GraphFlow 执行流程

```mermaid
sequenceDiagram
    participant User as 用户
    participant Builder as DiGraphBuilder
    participant Flow as GraphFlow
    participant Agent1 as 智能体1
    participant Agent2 as 智能体2
    participant Agent3 as 智能体3
    
    User->>Builder: 创建智能体
    Builder->>Builder: 添加节点
    Builder->>Builder: 添加边
    Builder->>Flow: 构建GraphFlow
    User->>Flow: 提交任务
    Flow->>Agent1: 分发任务
    Agent1->>Flow: 返回结果
    Flow->>Agent2: 分发任务
    Flow->>Agent3: 分发任务
    Agent2->>Flow: 返回结果
    Agent3->>Flow: 返回结果
    Flow->>User: 返回最终结果
```
