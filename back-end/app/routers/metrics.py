"""
Metrics router - API endpoints for metrics and KPIs (MongoDB/Beanie)
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.schemas import MetricResponse, KPIResponse, ProjectCodeResponse
from app.models import Deployment, Metric
from app.services.metrics_service import MetricsService

router = APIRouter()
metrics_service = MetricsService()


@router.get("/metrics/{deployment_id}", response_model=List[MetricResponse])
async def get_metrics(
    deployment_id: str,
    hours: int = Query(24, ge=1, le=168)
):
    """Get metrics history for a deployment"""
    deployment = await Deployment.find_one(
        Deployment.deployment_id == deployment_id
    )
    
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    metrics = await metrics_service.get_metrics_history(deployment_id, hours=hours)
    return metrics


@router.get("/metrics/{deployment_id}/kpis", response_model=KPIResponse)
async def get_kpis(deployment_id: str):
    """Get Key Performance Indicators for a deployment"""
    deployment = await Deployment.find_one(
        Deployment.deployment_id == deployment_id
    )
    
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    kpis = await metrics_service.calculate_kpis(deployment_id)
    return kpis


@router.get("/deployments/{deployment_id}/code", response_model=ProjectCodeResponse)
async def get_project_code(deployment_id: str):
    """Get generated project code/files for a deployment"""
    deployment = await Deployment.find_one(
        Deployment.deployment_id == deployment_id
    )
    
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    files = deployment.generated_files or {}
    
    return ProjectCodeResponse(
        deployment_id=deployment_id,
        files=files,
        file_list=list(files.keys()),
        total_files=len(files)
    )


@router.get("/deployments/{deployment_id}/code/diff")
async def get_code_diff(
    deployment_id: str,
    compare_to: Optional[str] = None
):
    """Get diff between current code and previous version"""
    deployment = await Deployment.find_one(
        Deployment.deployment_id == deployment_id
    )
    
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    current_files = deployment.generated_files or {}
    
    if compare_to:
        # Compare with another deployment
        compare_deployment = await Deployment.find_one(
            Deployment.deployment_id == compare_to
        )
        
        if not compare_deployment:
            raise HTTPException(status_code=404, detail="Comparison deployment not found")
        
        compare_files = compare_deployment.generated_files or {}
    else:
        # Return current files (no diff for now)
        compare_files = {}
    
    # Simple diff calculation (in production, use proper diff library)
    diff_result = {
        "added": [],
        "modified": [],
        "removed": [],
        "files": {}
    }
    
    all_files = set(current_files.keys()) | set(compare_files.keys())
    
    for file_path in all_files:
        current_content = current_files.get(file_path, "")
        compare_content = compare_files.get(file_path, "")
        
        if file_path not in compare_files:
            diff_result["added"].append(file_path)
            diff_result["files"][file_path] = {
                "status": "added",
                "content": current_content
            }
        elif file_path not in current_files:
            diff_result["removed"].append(file_path)
            diff_result["files"][file_path] = {
                "status": "removed",
                "content": compare_content
            }
        elif current_content != compare_content:
            diff_result["modified"].append(file_path)
            diff_result["files"][file_path] = {
                "status": "modified",
                "current": current_content,
                "previous": compare_content
            }
    
    return diff_result


@router.post("/metrics/{deployment_id}/record")
async def record_metrics(deployment_id: str, metrics_data: dict):
    """Record new metrics (called by agents or monitoring system)"""
    deployment = await Deployment.find_one(
        Deployment.deployment_id == deployment_id
    )
    
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    metric = await metrics_service.record_metrics(deployment_id, metrics_data)
    
    return {
        "message": "Metrics recorded",
        "metric_id": str(metric.id),
        "timestamp": metric.timestamp.isoformat()
    }
