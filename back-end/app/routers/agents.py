from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas import AgentTemplate, AgentType, MetricsResponse
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["agents"])

# Predefined agent templates
AGENT_TEMPLATES = [
    {
        "id": "customer-support-v1",
        "name": "Customer Support Agent",
        "description": "AI agent for handling customer inquiries, FAQs, and support tickets using LangChain",
        "agent_type": AgentType.CUSTOMER_SUPPORT,
        "framework": "LangChain",
        "use_cases": [
            "Answer frequently asked questions",
            "Handle basic support tickets",
            "Provide product information",
            "Route complex issues to human agents"
        ],
        "default_config": {
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 500
        }
    },
    {
        "id": "content-writer-v1",
        "name": "Content Writer Agent",
        "description": "AI agent for generating blog posts, articles, and marketing content using CrewAI",
        "agent_type": AgentType.CONTENT_WRITER,
        "framework": "CrewAI",
        "use_cases": [
            "Generate blog post ideas",
            "Write SEO-optimized articles",
            "Create social media content",
            "Draft marketing copy"
        ],
        "default_config": {
            "model": "gpt-4",
            "temperature": 0.8,
            "max_tokens": 2000
        }
    },
    {
        "id": "data-analyst-v1",
        "name": "Data Analyst Agent",
        "description": "AI agent for analyzing datasets and generating insights using AutoGen",
        "agent_type": AgentType.DATA_ANALYST,
        "framework": "AutoGen",
        "use_cases": [
            "Analyze CSV/Excel data",
            "Generate statistical summaries",
            "Create data visualizations",
            "Identify trends and patterns"
        ],
        "default_config": {
            "model": "gpt-4",
            "temperature": 0.3,
            "max_tokens": 1500
        }
    }
]


@router.get("/templates", response_model=List[AgentTemplate])
async def list_templates():
    """
    List all available agent templates.
    
    Returns predefined templates for customer support, content writing,
    and data analysis agents.
    """
    return AGENT_TEMPLATES


@router.get("/templates/{template_id}", response_model=AgentTemplate)
async def get_template(template_id: str):
    """
    Get details of a specific agent template.
    """
    template = next((t for t in AGENT_TEMPLATES if t["id"] == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.get("/metrics/{deployment_id}", response_model=MetricsResponse)
async def get_agent_metrics(deployment_id: str):
    """
    Get metrics for a deployed agent.
    
    Returns request count, error rate, response times, and uptime.
    """
    try:
        # In a real implementation, this would query MongoDB for metrics
        # For now, return mock data
        return MetricsResponse(
            deployment_id=deployment_id,
            request_count=1250,
            error_count=15,
            avg_response_time=0.45,
            uptime_percentage=99.2,
            last_updated=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))