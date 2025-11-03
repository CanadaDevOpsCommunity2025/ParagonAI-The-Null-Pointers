"""
Agents router - List available agent templates
"""

from fastapi import APIRouter
from app.models import AgentType

router = APIRouter()


@router.get("/agents")
async def list_agents():
    """List available agent templates"""
    return {
        "agents": [
            {
                "type": AgentType.CUSTOMER_SUPPORT.value,
                "name": "Customer Support Agent",
                "description": "Handles customer inquiries and support requests using LangChain",
                "framework": "LangChain"
            },
            {
                "type": AgentType.CONTENT_WRITER.value,
                "name": "Content Writer Agent",
                "description": "Generates content, blog posts, and articles using CrewAI",
                "framework": "CrewAI"
            },
            {
                "type": AgentType.DATA_ANALYST.value,
                "name": "Data Analyst Agent",
                "description": "Analyzes data and provides insights using AutoGen",
                "framework": "AutoGen"
            }
        ]
    }

