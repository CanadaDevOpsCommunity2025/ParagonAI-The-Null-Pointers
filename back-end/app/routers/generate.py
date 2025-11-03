"""
Code generation router - Generate agent code from prompts (MongoDB/Beanie)
"""

from fastapi import APIRouter, HTTPException
import uuid
from app.schemas import GenerateRequest, GenerateResponse
from app.models import Deployment, DeploymentStatus, AgentType
from app.services.prompt_engineer import PromptEngineer
from app.utils.genagent_core import GenAgentCore

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
async def generate_agent_code(request: GenerateRequest):
    """
    Generate agent code and infrastructure from a prompt
    Uses advanced prompt engineering to create deployment files
    """
    try:
        # Parse prompt to extract requirements
        gen_core = GenAgentCore()
        requirements = gen_core.parse_prompt(request.prompt)
        
        # Use explicit values from request if provided
        agent_type = request.agent_type or AgentType(requirements.get("agent_type", "customer_support"))
        requirements["agent_type"] = agent_type.value
        requirements["cloud_provider"] = request.cloud_provider or requirements.get("cloud_provider", "aws")
        requirements["scale"] = request.scale or requirements.get("scale", 2)
        requirements["container_platform"] = request.container_platform or requirements.get("container_platform", "kubernetes")
        
        # Generate code using prompt engineering
        prompt_engineer = PromptEngineer()
        generated_files = prompt_engineer.generate_infrastructure_code(
            prompt=request.prompt,
            agent_type=agent_type.value,
            requirements=requirements
        )
        
        # Create deployment record
        deployment_id = str(uuid.uuid4())[:8]
        name = request.name or f"{agent_type.value}-agent-{deployment_id}"
        
        deployment = Deployment(
            deployment_id=deployment_id,
            name=name,
            agent_type=agent_type,
            config=requirements,
            prompt=request.prompt,
            generated_files=generated_files,
            status=DeploymentStatus.PENDING,
            cloud_provider=requirements["cloud_provider"],
            cluster_name="paragonai-cluster",
            namespace="default"
        )
        
        await deployment.insert()
        
        return GenerateResponse(
            deployment_id=deployment_id,
            name=name,
            agent_type=agent_type.value,
            files=generated_files,
            requirements=requirements
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")
