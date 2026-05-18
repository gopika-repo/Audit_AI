from __future__ import annotations

import json
import asyncio
from typing import List, Optional
from uuid import uuid4
from datetime import datetime

from app.services.rag_service import get_rag_service, SearchResult
from app.clients.redis_client import get_redis
from app.services.prompt_service import build_rag_prompt
from app.services.llm_service import get_llm_service
from app.core.logging import get_logger

logger = get_logger()

CONVERSATION_TTL = 86400
MAX_HISTORY = 10


class ChatService:
    def __init__(self):
        self.rag = get_rag_service()
        self.llm = get_llm_service()

    async def chat(self, message: str, conversation_id: Optional[str] = None, user_id: Optional[str] = None) -> dict:
        # Ensure conversation id
        if not conversation_id:
            conversation_id = str(uuid4())

        # 1. Retrieve relevant context
        try:
            context_results = await self._retrieve_context(message)
        except Exception as exc:
            logger.error(f"Failed to retrieve context: {exc}")
            context_results = []

        # 2. Fetch conversation history
        history = await self.get_conversation_history(conversation_id)

        # 3. Build prompt
        prompt = build_rag_prompt(message, context_results, history)

        # 4. Call Gemini
        try:
            ai_response = await self.llm.generate(prompt)
        except Exception as exc:
            logger.error(f"LLM call failed: {exc}")
            ai_response = "An internal error occurred while generating the response."

        # 5. Save messages
        timestamp = datetime.utcnow().isoformat()
        user_msg = {"role": "user", "content": message, "timestamp": timestamp}
        assistant_msg = {"role": "assistant", "content": ai_response, "timestamp": timestamp, "sources": [r.to_dict() for r in context_results]}

        await self._save_message(conversation_id, user_msg)
        await self._save_message(conversation_id, assistant_msg)

        # Build response
        response = {
            "response": ai_response,
            "conversation_id": conversation_id,
            "sources": [r.to_dict() for r in context_results],
            "message_id": str(uuid4()),
            "timestamp": timestamp,
        }

        return response

    async def _retrieve_context(self, query: str) -> List[SearchResult]:
        try:
            results = await self.rag.search_similar(query=query, limit=5)
            return results
        except Exception as exc:
            logger.error(f"Context retrieval failed: {exc}")
            return []

    def _build_prompt(self, query: str, context: List[SearchResult], history: List[dict]) -> str:
        return build_rag_prompt(query, context, history)

    async def _generate_response(self, prompt: str) -> str:
        return await self.llm.generate(prompt)

    async def _save_message(self, conversation_id: str, message: dict) -> None:
        try:
            redis = get_redis()
            key = f"conversation:{conversation_id}"

            existing = await redis.get(key)
            if existing:
                messages = json.loads(existing)
            else:
                messages = []

            messages.append(message)

            # Trim to last MAX_HISTORY messages
            if len(messages) > MAX_HISTORY:
                messages = messages[-MAX_HISTORY:]

            await redis.set(key, json.dumps(messages), ex=CONVERSATION_TTL)
        except Exception as exc:
            logger.error(f"Failed to save message to Redis: {exc}")

    async def get_conversation_history(self, conversation_id: str) -> List[dict]:
        try:
            redis = get_redis()
            key = f"conversation:{conversation_id}"
            data = await redis.get(key)
            if not data:
                return []
            messages = json.loads(data)
            # Return list of dicts limited to MAX_HISTORY
            return messages[-MAX_HISTORY:]
        except Exception as exc:
            logger.error(f"Failed to read conversation history: {exc}")
            return []

    async def clear_conversation(self, conversation_id: str) -> None:
        try:
            redis = get_redis()
            key = f"conversation:{conversation_id}"
            await redis.delete(key)
        except Exception as exc:
            logger.error(f"Failed to clear conversation: {exc}")


_chat_service = None


def get_chat_service() -> ChatService:
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
