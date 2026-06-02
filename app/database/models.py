from sqlalchemy import (
    Column, String, Text, DateTime, Integer, ForeignKey, Boolean
)
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime
import uuid


class Base(DeclarativeBase):
    pass


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan",
        order_by="Message.created_at"
    )

    def __repr__(self):
        return f"<Conversation id={self.id} title={self.title}>"


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)           # "user" or "assistant" or "system"
    content = Column(Text, nullable=False)
    message_type = Column(String(20), default="text")   # "text" | "research" | "voice"
    created_at = Column(DateTime, default=datetime.utcnow)
    has_sources = Column(Boolean, default=False)

    conversation = relationship("Conversation", back_populates="messages")

    def to_llm_dict(self) -> dict:
        """Format for LLM API call."""
        return {"role": self.role, "content": self.content}

    def __repr__(self):
        return f"<Message id={self.id} role={self.role} len={len(self.content)}>"
