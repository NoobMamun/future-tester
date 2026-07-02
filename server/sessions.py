"""In-memory session store for chat history and dynamic counters."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ChatMessage:
    role: str  # "user" | "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class Session:
    id: str
    messages: list[ChatMessage] = field(default_factory=list)
    regret_count: int = 847
    best_decision_count: int = 12
    topics_discussed: set[str] = field(default_factory=set)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_stats(self) -> dict[str, Any]:
        return {
            "regret_count": self.regret_count,
            "best_decision_count": self.best_decision_count,
            "topics_discussed": sorted(self.topics_discussed),
            "message_count": len(self.messages),
        }


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def create(self) -> Session:
        session_id = str(uuid.uuid4())
        session = Session(id=session_id)
        self._sessions[session_id] = session
        return session

    def get(self, session_id: str | None) -> Session:
        if session_id and session_id in self._sessions:
            return self._sessions[session_id]
        return self.create()

    def get_existing(self, session_id: str) -> Session | None:
        return self._sessions.get(session_id)

    def add_message(self, session: Session, role: str, content: str) -> None:
        session.messages.append(ChatMessage(role=role, content=content))
        # Keep last 20 turns for context
        if len(session.messages) > 40:
            session.messages = session.messages[-40:]


store = SessionStore()
