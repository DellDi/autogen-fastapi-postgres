"""
旧版API路由 - 兼容性API端点
"""
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from autogen_agentchat.messages import TextMessage

from api.routes import chat
from api.services import ChatMessageService, ChatSessionService
from api.database import get_db

router = APIRouter(tags=["旧版API"])

@router.get("/")
async def root():
    """提供聊天界面HTML文件"""
    from fastapi.responses import FileResponse
    import os
    return FileResponse(os.path.join(os.path.dirname(os.path.dirname(__file__)), "example/app_agent.html"))

@router.get("/history")
async def history(
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """获取最新会话的历史记录（兼容旧API）"""
    try:
        # 获取最新会话
        session = await ChatSessionService.get_latest_session(db)
        if not session:
            return []
        
        # 获取会话消息
        messages = await ChatMessageService.get_session_messages(db, session.id)
        return await ChatMessageService.convert_to_dict_list(messages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/chat")
async def legacy_chat(
    request: TextMessage,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """发送消息并获取回复（兼容旧API）"""
    try:
        # 获取或创建最新会话
        session = await ChatSessionService.get_latest_session(db)
        if not session:
            session = await ChatSessionService.create_session(db)
            # 初始化agent_state
            from api.services import get_agent
            agent = await get_agent(db=db)
            state = await agent.save_state()
            await ChatSessionService.update_agent_state(db, session.id, state)
        
        # 调用新的聊天API
        return await chat(session.id, request, db)
    except Exception as e:
        error_message = {
            "type": "error",
            "content": f"Error: {str(e)}",
            "source": "system"
        }
        raise HTTPException(status_code=500, detail=error_message) from e
