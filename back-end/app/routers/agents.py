# In app/routers/agents.py
from fastapi import APIRouter, HTTPException, Body, Request
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.schemas import AgentTemplate, AgentType, MetricsResponse, AgentDefaultConfig
from datetime import datetime
import logging
from copy import deepcopy
import json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agents", tags=["agents"])

class UpdatePromptRequest(BaseModel):
    system_prompt: str
    agent_id: Optional[str] = None

# Predefined agent templates as dictionaries
AGENT_TEMPLATES_DATA = [
    {
        "id": "customer-support-v1",
        "name": "Customer Support Agent",
        "description": "AI agent for handling customer inquiries, FAQs, and support tickets using LangChain with Groq's Mixtral model",
        "agent_type": AgentType.CUSTOMER_SUPPORT,
        "framework": "LangChain",
        "use_cases": [
            "Answer frequently asked questions",
            "Handle basic support tickets",
            "Provide product information",
            "Route complex issues to human agents"
        ],
        "default_config": {
            "model": "mixtral-8x7b-32768",
            "temperature": 0.1,
            "max_tokens": 4096,
            "system_prompt": "You are a helpful customer support agent. Your goal is to assist users with their inquiries in a friendly and professional manner."
        }
    },
    {
        "id": "content-writer-v1",
        "name": "Content Writer Agent",
        "description": "AI agent for generating blog posts, articles, and marketing content using CrewAI with Groq's Mixtral model",
        "agent_type": AgentType.CONTENT_WRITER,
        "framework": "CrewAI",
        "use_cases": [
            "Generate blog post ideas",
            "Write SEO-optimized articles",
            "Create social media content",
            "Draft marketing copy"
        ],
        "default_config": {
            "model": "mixtral-8x7b-32768",
            "temperature": 0.1,
            "max_tokens": 4096,
            "system_prompt": "You are a creative content writer. Generate engaging and original content based on the user's requirements."
        }
    },
    {
        "id": "data-analyst-v1",
        "name": "Data Analyst Agent",
        "description": "AI agent for analyzing datasets and generating insights using AutoGen with Groq's Mixtral model",
        "agent_type": AgentType.DATA_ANALYST,
        "framework": "AutoGen",
        "use_cases": [
            "Analyze CSV/Excel data",
            "Generate statistical summaries",
            "Create data visualizations",
            "Identify trends and patterns"
        ],
        "default_config": {
            "model": "mixtral-8x7b-32768",
            "temperature": 0.1,
            "max_tokens": 4096,
            "system_prompt": "You are a data analyst. Analyze the provided data and provide clear, actionable insights."
        }
    }
]

# Test endpoint to verify the router is working
@router.get("/test", include_in_schema=True, response_model=dict)
async def test_endpoint():
    """Test endpoint to verify the agents router is working."""
    return {"message": "Agents router is working!"}
    
# Convert to Pydantic models
AGENT_TEMPLATES = [AgentTemplate(**template) for template in AGENT_TEMPLATES_DATA]

@router.get("/templates", response_model=List[AgentTemplate])
async def list_templates():
    """List all available agent templates."""
    return AGENT_TEMPLATES

@router.post("/templates", response_model=List[AgentTemplate])
async def create_template(template: AgentTemplate):
    """Create a new agent template."""
    AGENT_TEMPLATES.append(template)
    return AGENT_TEMPLATES

@router.get("/templates/{template_id}", response_model=AgentTemplate)
async def get_template(template_id: str):
    """Get details of a specific agent template."""
    template = next((t for t in AGENT_TEMPLATES if t.id == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.post("/update-template", include_in_schema=True)
async def update_agent_prompt(request: UpdatePromptRequest = Body(...)):
    """
    Update the system prompt for an agent.
    
    Args:
        agent_id: ID of the agent to update (if not provided, updates all agents)
        system_prompt: The new system prompt to use
    """
    try:
        updated = 0
        for i, template in enumerate(AGENT_TEMPLATES):
            if not request.agent_id or template.id == request.agent_id:
                # Create a new config with the updated prompt
                new_config = template.default_config.copy(update={
                    "system_prompt": request.system_prompt
                })
                # Update the template with the new config
                AGENT_TEMPLATES[i] = template.copy(update={
                    "default_config": new_config
                })
                updated += 1
                
        if updated == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Agent with ID {request.agent_id} not found"
            )
            
        return {"status": "success", "updated_agents": updated}
        
    except Exception as e:
        logger.error(f"Error updating prompt: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


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
            request_count=100,
            error_count=5,
            avg_response_time=0.5,
            uptime_percentage=99.9,
            last_updated=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))