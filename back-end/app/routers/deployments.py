"""
Deployments router - Manage agent deployments (MongoDB/Beanie)
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import uuid
from app.schemas import DeployRequest, DeployResponse, DeploymentStatusResponse, DeploymentListItem
from app.models import Deployment, DeploymentStatus, AgentType
from app.services.deployment_service import DeploymentService

router = APIRouter()
deployment_service = DeploymentService()


@router.post("/deploy", response_model=DeployResponse)
async def deploy_agent(request: DeployRequest):
    """Deploy an agent to AWS EKS"""
    try:
        # Find or create deployment
        if request.deployment_id:
            deployment = await Deployment.find_one(
                Deployment.deployment_id == request.deployment_id
            )
            if not deployment:
                raise HTTPException(status_code=404, detail="Deployment not found")
        else:
            # Create new deployment from config
            deployment = Deployment(
                deployment_id=str(uuid.uuid4())[:8],
                name=request.name,
                agent_type=request.agent_type,
                config=request.config,
                generated_files=request.generated_files,
                status=DeploymentStatus.PENDING
            )
            await deployment.insert()
        
        # Deploy to EKS
        result = await deployment_service.deploy_to_eks(
            deployment=deployment,
            generated_files=request.generated_files or deployment.generated_files
        )
        
        return DeployResponse(
            deployment_id=deployment.deployment_id,
            status=DeploymentStatus.RUNNING,
            message=result["message"],
            endpoints={"service": result.get("endpoint")}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deployment failed: {str(e)}")


@router.get("/deployments/{deployment_id}/status", response_model=DeploymentStatusResponse)
async def get_deployment_status(deployment_id: str):
    """Get deployment status"""
    try:
        status = await deployment_service.get_deployment_status(deployment_id)
        deployment = await Deployment.find_one(
            Deployment.deployment_id == deployment_id
        )
        
        if not deployment:
            raise HTTPException(status_code=404, detail="Deployment not found")
        
        return DeploymentStatusResponse(
            deployment_id=deployment.deployment_id,
            status=deployment.status,
            agent_type=deployment.agent_type.value,
            name=deployment.name,
            created_at=deployment.created_at,
            replicas=status.get("replicas"),
            endpoints=status.get("endpoints")
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/deployments/{deployment_id}/logs")
async def get_deployment_logs(
    deployment_id: str,
    tail: int = Query(100, ge=1, le=1000),
    since: str = Query("1h")
):
    """Get deployment logs"""
    try:
        logs = await deployment_service.get_logs(deployment_id, tail=tail, since=since)
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/deployments", response_model=List[DeploymentListItem])
async def list_deployments(
    status: Optional[DeploymentStatus] = None,
    agent_type: Optional[AgentType] = None
):
    """List all deployments with optional filters"""
    query = {}
    
    if status:
        query["status"] = status
    if agent_type:
        query["agent_type"] = agent_type
    
    if query:
        deployments = await Deployment.find(query).sort(-Deployment.created_at).to_list()
    else:
        deployments = await Deployment.find_all().sort(-Deployment.created_at).to_list()
    
    return deployments


@router.delete("/deployments/{deployment_id}")
async def delete_deployment(deployment_id: str):
    """Delete a deployment"""
    deployment = await Deployment.find_one(
        Deployment.deployment_id == deployment_id
    )
    
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    # In production, would also undeploy from EKS
    deployment.status = DeploymentStatus.STOPPED
    await deployment.save()
    
    return {"message": "Deployment stopped", "deployment_id": deployment_id}
