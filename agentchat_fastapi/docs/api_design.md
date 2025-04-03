# API 设计文档

## API 概述

本应用提供了一组RESTful API，用于管理会话和消息。同时保留了原有API以保持兼容性。

## 会话管理 API

### 获取会话列表

```
GET /sessions
```

**参数：**
- `limit`: 限制返回的会话数量，默认为10
- `offset`: 偏移量，用于分页，默认为0

**响应：**
```json
[
  {
    "id": "uuid-string",
    "name": "会话名称",
    "created_at": "2025-04-03T12:00:00",
    "updated_at": "2025-04-03T12:30:00",
    "agent_state": {},
    "messages_count": 10
  }
]
```

### 创建新会话

```
POST /sessions
```

**响应：**
```json
{
  "id": "uuid-string",
  "name": "新会话",
  "created_at": "2025-04-03T12:00:00",
  "updated_at": "2025-04-03T12:00:00",
  "agent_state": {},
  "messages_count": 0
}
```

### 获取会话详情

```
GET /sessions/{session_id}
```

**响应：**
```json
{
  "id": "uuid-string",
  "name": "会话名称",
  "created_at": "2025-04-03T12:00:00",
  "updated_at": "2025-04-03T12:30:00",
  "agent_state": {},
  "messages_count": 10
}
```

### 删除会话

```
DELETE /sessions/{session_id}
```

**响应：**
```json
{
  "success": true,
  "message": "会话已删除"
}
```

## 消息管理 API

### 获取会话历史记录

```
GET /sessions/{session_id}/history
```

**参数：**
- `limit`: 限制返回的消息数量，默认为100
- `offset`: 偏移量，用于分页，默认为0

**响应：**
```json
[
  {
    "id": "uuid-string",
    "session_id": "session-uuid-string",
    "source": "user",
    "content": "你好",
    "type": "TextMessage",
    "created_at": "2025-04-03T12:00:00",
    "models_usage": null,
    "metadata": {}
  },
  {
    "id": "uuid-string",
    "session_id": "session-uuid-string",
    "source": "assistant",
    "content": "你好！有什么我可以帮助你的吗？",
    "type": "TextMessage",
    "created_at": "2025-04-03T12:00:01",
    "models_usage": {
      "prompt_tokens": 10,
      "completion_tokens": 15
    },
    "metadata": {}
  }
]
```

### 发送消息并获取回复

```
POST /sessions/{session_id}/chat
```

**请求体：**
```json
{
  "source": "user",
  "content": "你好",
  "type": "TextMessage",
  "models_usage": null,
  "metadata": {}
}
```

**响应：**
```json
{
  "source": "assistant",
  "content": "你好！有什么我可以帮助你的吗？",
  "type": "TextMessage",
  "models_usage": {
    "prompt_tokens": 10,
    "completion_tokens": 15
  },
  "metadata": {}
}
```

## 兼容旧API

为了保持兼容性，保留了以下API：

### 获取历史记录（最新会话）

```
GET /history
```

**响应：**
与`GET /sessions/{session_id}/history`相同，但返回最新会话的历史记录。

### 发送消息并获取回复（最新会话）

```
POST /chat
```

**请求体和响应：**
与`POST /sessions/{session_id}/chat`相同，但使用最新会话。如果没有会话，则创建一个新会话。
