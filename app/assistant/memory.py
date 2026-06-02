from typing import List, Dict, Optional
import uuid

from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import Conversation, Message
from app.llm.prompts import JARVIS_SYSTEM_PROMPT
from app.services.settings import settings
from app.services.logger import get_logger

logger = get_logger("memory")


def create_conversation(title: Optional[str] = None) -> str:
    """Create a new conversation and return its ID."""
    with get_db() as db:
        conv = Conversation(id=str(uuid.uuid4()), title=title or "New Session")
        db.add(conv)
        db.flush()
        cid = conv.id
    logger.info(f"New conversation: {cid}")
    return cid


def save_message(
    conversation_id: str,
    role: str,
    content: str,
    message_type: str = "text",
    has_sources: bool = False,
) -> None:
    """Persist a message to the database."""
    with get_db() as db:
        # Create conversation row if it doesn't exist yet
        conv = db.get(Conversation, conversation_id)
        if conv is None:
            conv = Conversation(id=conversation_id, title="Session")
            db.add(conv)

        msg = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            message_type=message_type,
            has_sources=has_sources,
        )
        db.add(msg)


def load_context(
    conversation_id: str,
    max_messages: int = None,
) -> List[Dict[str, str]]:
    """
    Return the last N messages from a conversation formatted for the LLM,
    with the system prompt prepended.
    """
    max_messages = max_messages or settings.CONTEXT_WINDOW_MESSAGES

    # Build plain dicts INSIDE the session so attributes are always accessible
    with get_db() as db:
        rows = (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(max_messages)
            .all()
        )
        # Convert to plain dicts while session is still open
        raw = [{"role": r.role, "content": r.content} for r in rows]

    # Reverse so oldest-first
    raw.reverse()

    llm_messages = [{"role": "system", "content": JARVIS_SYSTEM_PROMPT}]
    for msg in raw:
        if msg["role"] in ("user", "assistant"):
            llm_messages.append(msg)

    return llm_messages


def get_recent_conversations(limit: int = 10) -> List[dict]:
    """Return a list of recent conversation summaries."""
    from sqlalchemy import func

    with get_db() as db:
        # Use COUNT subquery — avoids lazy-loading .messages outside session
        rows = (
            db.query(
                Conversation,
                func.count(Message.id).label("msg_count"),
            )
            .outerjoin(Message, Message.conversation_id == Conversation.id)
            .group_by(Conversation.id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": c.id,
                "title": c.title,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "updated_at": c.updated_at.isoformat() if c.updated_at else None,
                "message_count": count,
            }
            for c, count in rows
        ]


def get_conversation_messages(conversation_id: str) -> List[dict]:
    """Return all messages in a conversation for the frontend."""
    with get_db() as db:
        messages = (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
            .all()
        )
        return [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "type": m.message_type,
                "has_sources": m.has_sources,
                "timestamp": m.created_at.isoformat() if m.created_at else None,
            }
            for m in messages
        ]
