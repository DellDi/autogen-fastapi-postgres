# 物业智能体语义路由系统 API 接口设计

## 1. 用户入口接口

### POST /api/message
- 描述：用户发送自然语言请求，系统自动识别意图并分发到对应智能体
- 请求参数：
  - user_id: string
  - message: string
  - context_id: string（可选，多轮会话）
- 返回：
  - agent: string（路由到的智能体）
  - response: string（智能体回复）
  - context_id: string

## 2. 智能体注册与发现

### POST /api/agent/register
- 描述：Agent启动时注册到主控Host
- 请求参数：
  - name: string
  - label: string
  - code: string
  - keywords: list
  - sub_intents: list
- 返回：注册状态

### GET /api/agent/list
- 描述：查询所有已注册Agent
- 返回：Agent列表

## 3. 权限与角色管理

### POST /api/user/assign_role
- 描述：为用户分配角色
- 请求参数：
  - user_id: string
  - roles: list
- 返回：分配状态

### GET /api/user/agents
- 描述：查询用户可访问的Agent能力
- 请求参数：user_id: string
- 返回：可用Agent及意图列表

---

> 实际部署可按微服务/RESTful风格细化，支持异步消息、WebSocket等能力。
