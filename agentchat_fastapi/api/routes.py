"""
API路由 - 主要API端点
"""
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken

from api.services import get_agent
from api.models import ChatSession
from api.services import ChatMessageService, ChatSessionService
from api.database import get_db

router = APIRouter(tags=["会话管理"])

@router.get("/sessions")
async def list_sessions(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """获取会话列表"""
    try:
        sessions = await ChatSessionService.list_sessions(db, limit, offset)
        return [session.to_dict() for session in sessions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/sessions")
async def create_session(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """创建新会话"""
    try:
        session = await ChatSessionService.create_session(db)
        return session.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """获取会话详情"""
    try:
        session = await ChatSessionService.get_session(db, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        return session.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """删除会话"""
    try:
        success = await ChatSessionService.delete_session(db, session_id)
        if not success:
            raise HTTPException(status_code=404, detail="会话不存在")
        return {"success": True, "message": "会话已删除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/sessions/{session_id}/history")
async def get_history(
    session_id: UUID,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """获取会话历史记录"""
    try:
        # 检查会话是否存在
        session = await ChatSessionService.get_session(db, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        # 获取会话消息
        messages = await ChatMessageService.get_session_messages(db, session_id, limit, offset)
        return await ChatMessageService.convert_to_dict_list(messages)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/sessions/{session_id}/chat")
async def chat(
    session_id: UUID,
    request: TextMessage,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """发送消息并获取回复"""
    try:
        # 检查会话是否存在
        session = await ChatSessionService.get_session(db, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        # 保存用户消息
        await ChatMessageService.create_from_text_message(db, session_id, request)
        
        # 获取智能体并响应消息
        agent = await get_agent(session_id, db)
        response = await agent.on_messages(messages=[request], cancellation_token=CancellationToken())
        
        # 保存智能体状态
        state = await agent.save_state()
        
        # 确保状态包含必要的字段
        if "type" not in state:
            state["type"] = "AssistantAgentState"
        if "version" not in state:
            state["version"] = "1.0.0"
        if "llm_context" not in state:
            state["llm_context"] = {"messages": []}
            
        await ChatSessionService.update_agent_state(db, session_id, state)
        
        # 保存智能体回复
        assert isinstance(response.chat_message, TextMessage)
        await ChatMessageService.create_from_text_message(db, session_id, response.chat_message)
        
        return response.chat_message.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        error_message = {
            "type": "error",
            "content": f"Error: {str(e)}",
            "source": "system"
        }
        raise HTTPException(status_code=500, detail=error_message) from e
