from __future__ import annotations

import asyncio
from typing import List, AsyncGenerator

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger()
settings = get_settings()


class LLMService:
    def __init__(self):
        self.model_name = "llama-3.1-8b-instant"
        self.temperature = 0.7
        self.max_output_tokens = 1024
        self._configure()

    def _configure(self):
        key = getattr(settings, "GROQ_API_KEY", "")
        if not key:
            logger.warning("GROQ_API_KEY not set — using mock responses")
            self.use_mock = True
            self.client = None
        else:
            from groq import Groq
            self.client = Groq(api_key=key)
            self.use_mock = False
            logger.info(f"LLMService: Groq configured with model {self.model_name}")

    async def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        if self.use_mock:
            return "Mock response — set GROQ_API_KEY in .env to enable real AI responses."

        for attempt in range(3):
            try:
                def call():
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=max_tokens,
                        temperature=self.temperature,
                    )
                    return response.choices[0].message.content

                result = await asyncio.to_thread(call)

                if result:
                    logger.info(f"LLM response generated on attempt {attempt + 1}")
                    return result

                logger.warning("Empty response from Groq")
                return "I could not generate a response. Please try again."

            except Exception as exc:
                msg = str(exc).lower()
                logger.error(f"Groq error attempt {attempt + 1}/3: {exc}")

                if any(x in msg for x in ["rate", "429", "too many", "quota"]):
                    wait_time = (attempt + 1) * 5
                    logger.warning(f"Rate limit — waiting {wait_time}s")
                    await asyncio.sleep(wait_time)
                    continue

                if any(x in msg for x in ["decommissioned", "not supported", "invalid model"]):
                    logger.error(f"Model {self.model_name} not available")
                    return "Model configuration error. Please contact support."

                if any(x in msg for x in ["api key", "invalid", "unauthorized", "403"]):
                    logger.error("Invalid Groq API key")
                    return "API key error — check GROQ_API_KEY in .env."

                return "An error occurred. Please try again."

        return "Service busy. Please wait 30 seconds and try again."

    async def generate_with_history(self, messages: List[dict]) -> str:
        formatted = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            if role in ["user", "assistant", "system"]:
                formatted.append({"role": role, "content": content})

        if not formatted:
            return "No messages to process."

        if self.use_mock:
            return "Mock response — set GROQ_API_KEY in .env to enable real AI responses."

        try:
            def call():
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=formatted,
                    max_tokens=self.max_output_tokens,
                    temperature=self.temperature,
                )
                return response.choices[0].message.content

            result = await asyncio.to_thread(call)
            return result or "No response generated."

        except Exception as exc:
            logger.error(f"Groq history generation error: {exc}")
            if formatted:
                return await self.generate(formatted[-1]["content"])
            return "An error occurred. Please try again."

    async def stream_generate(self, prompt: str) -> AsyncGenerator[str, None]:
        text = await self.generate(prompt)
        yield text


_llm_service = None


def get_llm_service() -> LLMService:
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service