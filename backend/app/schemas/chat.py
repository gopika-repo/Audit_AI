from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime
    sources: Optional[List[dict]] = []


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    sources: List[dict]
    message_id: str
    timestamp: datetime


class ConversationHistory(BaseModel):
    conversation_id: str
    messages: List[ChatMessage]
    total: int
