"""
API路由 - 主要API端点
"""
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken

from agentchat_fastapi.api.services import get_agent, ChatMessageService, ChatSessionService
from agentchat_fastapi.api.models import ChatSession
from agentchat_fastapi.api.database import get_db

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
        # 使用事务包装创建会话操作
        session = ChatSession(
            name="新会话",
            agent_state={
                "type": "AssistantAgentState",
                "version": "1.0.0",
                "llm_context": {
                    "messages": []
                }
            }
        )
        db.add(session)
        await db.flush()
        await db.commit()  # 显式提交事务
        return session.to_dict()
    except Exception as e:
        # 记录详细错误信息
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"创建会话错误: {error_detail}")
        await db.rollback()  # 显式回滚事务
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
        # 先查询会话是否存在
        session = await ChatSessionService.get_session(db, session_id)
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")
            
        # 使用ORM方式删除会话（级联删除会自动处理关联的消息）
        await db.delete(session)
        
        # 提交事务
        await db.commit()
        
        return {"success": True, "message": "会话已删除"}
    except HTTPException:
        raise
    except Exception as e:
        # 记录详细错误信息以便调试
        print(f"删除会话错误: {str(e)}")
        await db.rollback()
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
        
        # 记录详细的调试信息
        print(f"Response type: {type(response)}")
        print(f"Response content: {response.content if hasattr(response, 'content') else 'No content'}")
        print(f"Response attributes: {dir(response)}")
        if hasattr(response, 'models_usage'):
            print(f"Models usage type: {type(response.models_usage)}")
            print(f"Models usage attributes: {dir(response.models_usage) if response.models_usage else 'None'}")
        if hasattr(response, 'metadata') and response.metadata:
            print(f"Metadata: {response.metadata}")
        if hasattr(response, 'meta_data') and response.meta_data:
            print(f"Meta data: {response.meta_data}")
        
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
        
        # 提交事务，确保所有更改都被保存到数据库
        await db.commit()
        
        # 手动创建响应字典，而不是调用to_dict方法
        if hasattr(response.chat_message, 'to_dict'):
            # 如果对象有to_dict方法，使用它
            result = response.chat_message.to_dict()
        else:
            # 否则手动创建字典
            result = {
                "content": response.chat_message.content if hasattr(response.chat_message, 'content') else "",
                "source": response.chat_message.source if hasattr(response.chat_message, 'source') else "assistant",
                "type": response.chat_message.type if hasattr(response.chat_message, 'type') else "TextMessage",
                "models_usage": response.chat_message.models_usage if hasattr(response.chat_message, 'models_usage') else None,
                "metadata": response.chat_message.metadata if hasattr(response.chat_message, 'metadata') else {}
            }
            # 添加thought字段（如果存在）
            if hasattr(response.chat_message, 'thought') and response.chat_message.thought:
                result["thought"] = response.chat_message.thought
        
        return result
    except Exception as e:
        # 记录详细的错误信息
        import traceback
        print(f"Error in chat endpoint: {str(e)}")
        print(traceback.format_exc())
        error_message = {
            "type": "error",
            "content": f"Error: {str(e)}",
            "source": "system"
        }
        raise HTTPException(status_code=500, detail=error_message) from e
