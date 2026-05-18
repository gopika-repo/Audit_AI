from __future__ import annotations

from typing import List
from datetime import datetime

SYSTEM_PROMPT = """
You are an expert AI engineering mentor for our company.
You help new engineers understand our projects, tech stack,
architecture decisions, and engineering practices.

You have access to our company knowledge base which includes:
- Project descriptions and purposes
- Tech stacks used in each project
- Engineering domains and AI categories
- Architecture and implementation details

RULES:
1. Always answer based on the provided context
2. If context doesn't contain the answer, say so honestly
3. Be specific about which project you're referring to
4. Explain technical concepts clearly for new engineers
5. When mentioning tech stack, explain WHY it was chosen
6. Always be encouraging and educational in tone
"""

from app.services.rag_service import SearchResult


def format_context(search_results: List[SearchResult]) -> str:
    if not search_results:
        return "(no context found)"

    parts = []
    for r in search_results:
        parts.append(
            f"Project: {r.project_name}\nChunkType: {r.chunk_type}\nContent: {r.content}\nScore: {r.score:.3f}\n"
        )
    return "\n---\n".join(parts)


def format_history(messages: List[dict]) -> str:
    if not messages:
        return ""
    parts = []
    for m in messages:
        parts.append(f"{m.get('role')}: {m.get('content')}")
    return "\n".join(parts)


def build_rag_prompt(query: str, context_chunks: List[SearchResult], history: List[dict]) -> str:
    # System prompt first
    ctx = format_context(context_chunks)
    hist = format_history(history)

    prompt = SYSTEM_PROMPT + "\n\n"
    prompt += "Context:\n" + ctx + "\n\n"
    if hist:
        prompt += "Conversation History:\n" + hist + "\n\n"
    prompt += f"Question: {query}\n\nAnswer as an expert engineer, citing project names when relevant."

    return prompt
