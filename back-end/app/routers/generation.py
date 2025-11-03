from fastapi import APIRouter, HTTPException
from app.schemas import GenerateRequest, GenerateResponse
from app.services.deployment_service import deployment_service
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/generation", tags=["generation"])


@router.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
    try:
        result = deployment_service.generate_full_deployment(
            prompt=req.prompt,
            agent_type=req.agent_type,
            cloud_provider=req.cloud_provider,
            enable_monitoring=req.enable_monitoring,
            enable_cicd=req.enable_cicd,
            enable_security_scan=req.enable_security_scan,
        )

        if result.get("status") == "failed":
            raise HTTPException(status_code=500, detail=result.get("error", "Generation failed"))

        return GenerateResponse(
            generation_id=result["generation_id"],
            status="success",
            message="Generation completed",
            files_generated=result.get("files_generated", []),
            download_url=None,
        )
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.schemas import GenerateRequest, GenerateResponse
from app.services.deployment_service import deployment_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/generate", tags=["generation"])


@router.post("/", response_model=GenerateResponse)
async def generate_deployment(request: GenerateRequest, background_tasks: BackgroundTasks):
    """
    Generate complete deployment package from natural language prompt.
    
    This endpoint:
    - Parses the user's deployment requirements
    - Generates agent code, Dockerfile, K8s manifests
    - Creates CI/CD pipelines and monitoring configs
    - Returns a package ready for deployment
    """
    try:
        logger.info(f"Received generation request: {request.prompt[:100]}...")
        
        result = deployment_service.generate_full_deployment(
            prompt=request.prompt,
            agent_type=request.agent_type,
            cloud_provider=request.cloud_provider,
            enable_monitoring=request.enable_monitoring,
            enable_cicd=request.enable_cicd,
            enable_security_scan=request.enable_security_scan
        )
        
        if result["status"] == "failed":
            raise HTTPException(status_code=500, detail=result.get("error", "Generation failed"))
        
        return GenerateResponse(
            generation_id=result["generation_id"],
            status="success",
            message=f"Generated {len(result['files_generated'])} files successfully",
            files_generated=result["files_generated"],
            download_url=f"/api/v1/generate/{result['generation_id']}/download"
        )
    
    except Exception as e:
        logger.error(f"Generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))