from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas import (
    DeploymentRequest, DeploymentResponse, DeploymentInfo,
    RollbackRequest, DeploymentStatus
)
from app.services.deployment_service import deployment_service
from app.services.kubernetes_service import kubernetes_service
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/deployments", tags=["deployments"])


@router.post("/", response_model=DeploymentResponse)
async def create_deployment(request: DeploymentRequest):
    """
    Deploy a generated agent to Kubernetes cluster.
    
    Takes a generation_id and deploys the generated application
    to the specified cloud provider and cluster.
    """
    try:
        logger.info(f"Deploying generation {request.generation_id}")
        
        result = deployment_service.deploy_to_kubernetes(
            generation_id=request.generation_id,
            namespace=request.namespace,
            replicas=request.replicas
        )
        
        if result["status"] == "failed":
            raise HTTPException(status_code=500, detail=result.get("error", "Deployment failed"))
        
        deployment_id = str(uuid.uuid4())
        
        return DeploymentResponse(
            deployment_id=deployment_id,
            status=DeploymentStatus.RUNNING if result["status"] == "deployed" else DeploymentStatus.DEPLOYING,
            message="Deployment successful" if result["status"] == "deployed" else "Deployment in progress",
            endpoint=result.get("endpoint"),
            dashboard_url=f"/api/v1/deployments/{deployment_id}/metrics"
        )
    
    except Exception as e:
        logger.error(f"Deployment failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{deployment_id}", response_model=DeploymentInfo)
async def get_deployment(deployment_id: str):
    """
    Get deployment information and status.
    """
    try:
        # In a real implementation, this would query MongoDB
        # For now, return a mock response
        raise HTTPException(status_code=404, detail="Deployment not found")
    except Exception as e:
        logger.error(f"Failed to get deployment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{deployment_id}")
async def delete_deployment(deployment_id: str, namespace: str = "default"):
    """
    Delete a deployment from Kubernetes.
    """
    try:
        # In a real implementation, extract app_name from deployment record
        app_name = "agent-app"  # Placeholder
        
        success = kubernetes_service.delete_resource("deployment", app_name, namespace)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete deployment")
        
        kubernetes_service.delete_resource("service", f"{app_name}-service", namespace)
        
        return {"message": "Deployment deleted successfully"}
    
    except Exception as e:
        logger.error(f"Failed to delete deployment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{deployment_id}/rollback")
async def rollback_deployment(deployment_id: str, request: RollbackRequest):
    """
    Rollback deployment to a previous version.
    """
    try:
        # In a real implementation, extract app_name and namespace from deployment record
        app_name = "agent-app"  # Placeholder
        namespace = "default"
        
        revision = int(request.target_version) if request.target_version else None
        success = kubernetes_service.rollback_deployment(app_name, namespace, revision)
        
        if not success:
            raise HTTPException(status_code=500, detail="Rollback failed")
        
        return {"message": "Rollback successful"}
    
    except Exception as e:
        logger.error(f"Rollback failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))