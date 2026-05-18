from __future__ import annotations

from typing import List
from fastapi import APIRouter, HTTPException, status
from app.schemas.chat import ChatRequest, ChatResponse, ConversationHistory
from app.services.chat_service import get_chat_service
from app.clients.redis_client import get_redis
from app.core.logging import get_logger

logger = get_logger()
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/message", response_model=ChatResponse)
async def post_message(request: ChatRequest):
    try:
        chat_service = get_chat_service()
        result = await chat_service.chat(
            message=request.message,
            conversation_id=request.conversation_id,
            user_id=request.user_id,
        )

        return ChatResponse(
            response=result["response"],
            conversation_id=result["conversation_id"],
            sources=result["sources"],
            message_id=result["message_id"],
            timestamp=result["timestamp"],
        )

    except Exception as exc:
        logger.error(f"Chat message failed: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Chat failed")


@router.get("/history/{conversation_id}", response_model=ConversationHistory)
async def get_history(conversation_id: str):
    try:
        chat_service = get_chat_service()
        messages = await chat_service.get_conversation_history(conversation_id)
        return ConversationHistory(conversation_id=conversation_id, messages=messages, total=len(messages))
    except Exception as exc:
        logger.error(f"Get history failed: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get history")


@router.delete("/history/{conversation_id}")
async def delete_history(conversation_id: str):
    try:
        chat_service = get_chat_service()
        await chat_service.clear_conversation(conversation_id)
        return {"status": "ok", "conversation_id": conversation_id}
    except Exception as exc:
        logger.error(f"Delete history failed: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete history")


@router.get("/conversations", response_model=List[str])
async def list_conversations():
    try:
        redis = get_redis()
        keys = await redis.keys("conversation:*")
        # strip prefix
        ids = [k.split(":", 1)[1] for k in keys]
        return ids
    except Exception as exc:
        logger.error(f"List conversations failed: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list conversations")
