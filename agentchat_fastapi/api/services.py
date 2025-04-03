"""
服务层 - 处理数据库操作和智能体交互
"""
import os
import uuid
from typing import Any, Dict, List, Optional

import aiofiles
import yaml
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_core.models import ChatCompletionClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models import ChatMessage, ChatSession
from api.database import get_db

# 模型配置路径
model_config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model_config.yaml")

async def get_agent(
    session_id: Optional[uuid.UUID] = None,
    db: AsyncSession = None
) -> AssistantAgent:
    """获取智能体，从数据库加载状态"""
    # 获取模型客户端配置
    async with aiofiles.open(model_config_path, "r") as file:
        model_config = yaml.safe_load(await file.read())
    model_client = ChatCompletionClient.load_component(model_config)
    
    # 创建智能体
    agent = AssistantAgent(
        name="assistant",
        model_client=model_client,
        system_message="You are a helpful assistant.",
    )
    
    # 如果提供了会话ID，则从数据库加载状态
    if session_id and db:
        session = await ChatSessionService.get_session(db, session_id)
        if session and session.agent_state:
            await agent.load_state(session.agent_state)
    
    return agent


class ChatSessionService:
    """聊天会话服务"""
    
    @staticmethod
    async def create_session(
        db: AsyncSession, name: str = "新会话", agent_state: Optional[Dict[str, Any]] = None
    ) -> ChatSession:
        """创建新会话"""
        # 确保agent_state包含必要的字段
        if agent_state is None:
            agent_state = {
                "type": "AssistantAgentState",
                "version": "1.0.0",
                "llm_context": {
                    "messages": []
                }
            }
        elif "type" not in agent_state:
            agent_state["type"] = "AssistantAgentState"
        elif "version" not in agent_state:
            agent_state["version"] = "1.0.0"
        elif "llm_context" not in agent_state:
            agent_state["llm_context"] = {"messages": []}
            
        session = ChatSession(
            name=name,
            agent_state=agent_state
        )
        db.add(session)
        await db.flush()
        return session
    
    @staticmethod
    async def get_session(db: AsyncSession, session_id: uuid.UUID) -> Optional[ChatSession]:
        """获取会话"""
        result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
        return result.scalars().first()
    
    @staticmethod
    async def get_latest_session(db: AsyncSession) -> Optional[ChatSession]:
        """获取最新会话"""
        result = await db.execute(
            select(ChatSession).order_by(ChatSession.updated_at.desc()).limit(1)
        )
        return result.scalars().first()
    
    @staticmethod
    async def list_sessions(db: AsyncSession, limit: int = 10, offset: int = 0) -> List[ChatSession]:
        """列出会话"""
        result = await db.execute(
            select(ChatSession)
            .order_by(ChatSession.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def update_agent_state(
        db: AsyncSession, session_id: uuid.UUID, agent_state: Dict[str, Any]
    ) -> Optional[ChatSession]:
        """更新智能体状态"""
        session = await ChatSessionService.get_session(db, session_id)
        if session:
            # 确保保留关键字段
            if "type" not in agent_state and session.agent_state and "type" in session.agent_state:
                agent_state["type"] = session.agent_state["type"]
            else:
                agent_state["type"] = "AssistantAgentState"
                
            if "version" not in agent_state and session.agent_state and "version" in session.agent_state:
                agent_state["version"] = session.agent_state["version"]
            else:
                agent_state["version"] = "1.0.0"
                
            if "llm_context" not in agent_state:
                agent_state["llm_context"] = {"messages": []}
                
            session.agent_state = agent_state
            db.add(session)
            await db.flush()
        return session
    
    @staticmethod
    async def delete_session(db: AsyncSession, session_id: uuid.UUID) -> bool:
        """删除会话"""
        session = await ChatSessionService.get_session(db, session_id)
        if session:
            await db.delete(session)
            return True
        return False
    
    @staticmethod
    async def update_session_name_from_messages(db: AsyncSession, session_id: uuid.UUID) -> Optional[ChatSession]:
        """根据消息更新会话名称"""
        session = await ChatSessionService.get_session(db, session_id)
        if session:
            new_name = session.generate_name_from_first_message()
            if new_name != session.name:
                session.name = new_name
                db.add(session)
                await db.flush()
        return session
    
    @staticmethod
    async def get_agent_state_messages(db: AsyncSession, session_id: uuid.UUID) -> List[Dict[str, Any]]:
        """获取智能体状态中的消息列表"""
        session = await ChatSessionService.get_session(db, session_id)
        if not session or not session.agent_state or "llm_context" not in session.agent_state:
            return []
            
        llm_context = session.agent_state.get("llm_context", {})
        return llm_context.get("messages", [])


class ChatMessageService:
    """聊天消息服务"""
    
    @staticmethod
    async def create_message(
        db: AsyncSession,
        session_id: uuid.UUID,
        source: str,
        content: str,
        message_type: str = "TextMessage",
        thought: Optional[str] = None,
        models_usage: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatMessage:
        """创建新消息"""
        message = ChatMessage(
            session_id=session_id,
            source=source,
            content=content,
            type=message_type,
            thought=thought,
            models_usage=models_usage,
            metadata=metadata or {}
        )
        db.add(message)
        await db.flush()
        
        # 如果是会话的第一条消息，更新会话名称
        session = await ChatSessionService.get_session(db, session_id)
        if session and len(session.messages) == 1:
            await ChatSessionService.update_session_name_from_messages(db, session_id)
        
        return message
    
    @staticmethod
    async def create_from_text_message(
        db: AsyncSession, session_id: uuid.UUID, message: TextMessage
    ) -> ChatMessage:
        """从TextMessage创建消息"""
        # 尝试从message中提取thought字段
        thought = None
        if hasattr(message, 'thought'):
            thought = message.thought
        
        return await ChatMessageService.create_message(
            db=db,
            session_id=session_id,
            source=message.source,
            content=message.content,
            message_type=message.type,
            thought=thought,
            models_usage=message.models_usage,
            metadata=message.metadata
        )
    
    @staticmethod
    async def get_session_messages(
        db: AsyncSession, session_id: uuid.UUID, limit: int = 100, offset: int = 0
    ) -> List[ChatMessage]:
        """获取会话消息"""
        result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def convert_to_dict_list(messages: List[ChatMessage]) -> List[Dict[str, Any]]:
        """转换为字典列表"""
        return [message.to_dict() for message in messages]
    
    @staticmethod
    async def convert_to_text_messages(messages: List[ChatMessage]) -> List[TextMessage]:
        """转换为TextMessage列表"""
        text_messages = []
        for msg in messages:
            # 创建基本的TextMessage
            text_msg = TextMessage(
                source=msg.source,
                content=msg.content,
                type=msg.type,
                models_usage=msg.models_usage,
                metadata=msg.metadata
            )
            
            # 如果有thought字段，添加到TextMessage中
            if msg.thought:
                text_msg.thought = msg.thought
                
            text_messages.append(text_msg)
            
        return text_messages
