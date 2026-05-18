"""Database seed entry point for company projects."""

from __future__ import annotations

import asyncio
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.session import get_async_session_maker, init_db_engine, close_db_engine
from app.models.project import Project

logger = get_logger()

PROJECT_SEEDS: list[dict[str, Any]] = [
    {
        "name": "Hand Gesture Control",
        "domain": "Computer Vision",
        "ai_category": "Deep Learning",
        "tech_stack": {
            "languages": ["Python"],
            "frameworks": ["OpenCV", "MediaPipe", "TensorFlow"],
            "tools": ["Jupyter"],
        },
        "description": "Real-time hand gesture recognition system for controlling computer interfaces using computer vision and deep learning.",
    },
    {
        "name": "Fake News Detector",
        "domain": "NLP",
        "ai_category": "Classification",
        "tech_stack": {
            "languages": ["Python"],
            "frameworks": ["HuggingFace", "FastAPI", "scikit-learn"],
            "tools": ["Streamlit"],
        },
        "description": "ML-powered system to detect and classify fake news articles using NLP techniques and transformer models.",
    },
    {
        "name": "Autonomous Freelance Project Tracker",
        "domain": "Agentic AI",
        "ai_category": "AI Agents",
        "tech_stack": {
            "languages": ["Python"],
            "frameworks": ["LangChain", "FastAPI", "PostgreSQL"],
            "tools": ["Docker", "Redis"],
        },
        "description": "AI agent that autonomously tracks freelance projects, manages deadlines, and generates progress reports.",
    },
    {
        "name": "WhatsApp Business Dashboard",
        "domain": "Business Intelligence",
        "ai_category": "Analytics",
        "tech_stack": {
            "languages": ["Python", "JavaScript"],
            "frameworks": ["FastAPI", "React", "PostgreSQL"],
            "tools": ["Docker", "Twilio API"],
        },
        "description": "Analytics dashboard for WhatsApp Business accounts with AI-powered insights and automated response management.",
    },
    {
        "name": "Career Path Simulation Agent",
        "domain": "Agentic AI",
        "ai_category": "AI Agents",
        "tech_stack": {
            "languages": ["Python"],
            "frameworks": ["LangGraph", "FastAPI", "OpenAI"],
            "tools": ["Qdrant", "Redis"],
        },
        "description": "AI agent that simulates career paths for students using market data and personalized recommendations.",
    },
    {
        "name": "MCP Personal Assistant",
        "domain": "Agentic AI",
        "ai_category": "MCP",
        "tech_stack": {
            "languages": ["Python"],
            "frameworks": ["MCP", "Claude API", "FastAPI"],
            "tools": ["Docker"],
        },
        "description": "Personal AI assistant built using Model Context Protocol for tool use and context management.",
    },
    {
        "name": "Money Mate",
        "domain": "FinTech",
        "ai_category": "Analytics",
        "tech_stack": {
            "languages": ["Python", "JavaScript"],
            "frameworks": ["FastAPI", "React", "PostgreSQL"],
            "tools": ["Docker", "Plaid API"],
        },
        "description": "Personal finance management app with AI-powered expense tracking, budgeting, and financial insights.",
    },
    {
        "name": "Research Agent",
        "domain": "Agentic AI",
        "ai_category": "AI Agents",
        "tech_stack": {
            "languages": ["Python"],
            "frameworks": ["LangGraph", "OpenAI", "Qdrant", "FastAPI"],
            "tools": ["Docker", "Redis"],
        },
        "description": "Autonomous research agent that searches, summarizes, and synthesizes information from multiple sources.",
    },
    {
        "name": "Chatbot",
        "domain": "Conversational AI",
        "ai_category": "LLM",
        "tech_stack": {
            "languages": ["Python"],
            "frameworks": ["FastAPI", "OpenAI", "LangChain"],
            "tools": ["Redis", "Docker"],
        },
        "description": "Intelligent conversational chatbot with context memory, multi-turn dialogue, and RAG-powered responses.",
    },
    {
        "name": "Code Reviewer",
        "domain": "Developer Tools",
        "ai_category": "LLM",
        "tech_stack": {
            "languages": ["Python"],
            "frameworks": ["FastAPI", "Claude API", "GitHub API"],
            "tools": ["Docker"],
        },
        "description": "AI-powered code review system that analyzes pull requests, suggests improvements, and enforces coding standards.",
    },
    {
        "name": "Multimodal Document Analysis",
        "domain": "Document AI",
        "ai_category": "Multimodal",
        "tech_stack": {
            "languages": ["Python"],
            "frameworks": ["FastAPI", "OpenAI Vision", "LangChain"],
            "tools": ["Qdrant", "Docker"],
        },
        "description": "Document analysis system supporting text, images, and tables using multimodal AI for extraction and summarization.",
    },
    {
        "name": "Stock Market Analyzer",
        "domain": "FinTech",
        "ai_category": "Analytics",
        "tech_stack": {
            "languages": ["Python"],
            "frameworks": ["FastAPI", "OpenAI", "Pandas"],
            "tools": ["Redis", "PostgreSQL"],
        },
        "description": "AI-powered stock market analysis tool with real-time data processing, trend detection, and investment insights.",
    },
]


async def seed_projects(session: AsyncSession) -> None:
    """Insert the default company projects if they are not already present."""

    existing_result = await session.execute(select(Project.name))
    existing_names = {name.lower() for name in existing_result.scalars().all()}

    inserted_names: list[str] = []
    for seed in PROJECT_SEEDS:
        project_name = seed["name"]
        if project_name.lower() in existing_names:
            logger.info("Skipping existing project: %s", project_name)
            print(f"Skipping existing project: {project_name}")
            continue

        session.add(
            Project(
                name=project_name,
                description=seed["description"],
                domain=seed["domain"],
                ai_category=seed["ai_category"],
                tech_stack=seed["tech_stack"],
                repo_url=None,
                is_active=True,
            )
        )
        inserted_names.append(project_name)
        existing_names.add(project_name.lower())

    if not inserted_names:
        print("No new projects inserted.")
        logger.info("Project seeding skipped because all projects already exist")
        return

    await session.commit()

    for project_name in inserted_names:
        print(f"Inserted project: {project_name}")
        logger.info("Inserted project: %s", project_name)

    print(f"Seeded {len(inserted_names)} project(s) successfully.")
    logger.info("Seeded %s project(s) successfully", len(inserted_names))


async def main() -> None:
    """Seed the database with the default project set."""

    # Initialize the DB engine/session maker so seed can run standalone
    await init_db_engine()
    try:
        session_maker = get_async_session_maker()
        async with session_maker() as session:
            await seed_projects(session)
    finally:
        await close_db_engine()


if __name__ == "__main__":
    asyncio.run(main())
