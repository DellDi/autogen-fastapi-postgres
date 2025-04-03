"""
数据库模型 - ORM模型定义
"""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import ForeignKey, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """基础模型类"""
    pass


class ChatSession(Base):
    """聊天会话模型"""
    __tablename__ = "chat_sessions"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, default="新会话")
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=text("now()"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=text("now()"), onupdate=func.now(), nullable=False
    )
    agent_state: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=True, default=dict)
    
    # 关系
    messages: Mapped[List["ChatMessage"]] = relationship(
        "ChatMessage", back_populates="session", cascade="all, delete", lazy="selectin"
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": str(self.id),
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "message_count": len(self.messages) if self.messages else 0
        }
    
    def generate_name_from_first_message(self) -> str:
        """根据第一条消息生成会话名称"""
        if not self.messages:
            return self.name
            
        # 找到第一条用户消息
        user_messages = [msg for msg in self.messages if msg.source == "user"]
        if not user_messages:
            return self.name
            
        first_message = user_messages[0]
        content = first_message.content
        
        # 截取前20个字符作为会话名称
        if len(content) > 20:
            return content[:20] + "..."
        return content


class ChatMessage(Base):
    """聊天消息模型"""
    __tablename__ = "chat_messages"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="CASCADE")
    )
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    thought: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=text("now()"), nullable=False
    )
    models_usage: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    
    # 关系
    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="messages")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "id": str(self.id),
            "session_id": str(self.session_id),
            "source": self.source,
            "content": self.content,
            "type": self.type,
            "created_at": self.created_at.isoformat(),
            "models_usage": self.models_usage,
            "metadata": self.metadata
        }
        
        # 只有当thought存在时才添加到结果中
        if self.thought:
            result["thought"] = self.thought
            
        return result
