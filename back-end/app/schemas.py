"""
Pydantic schemas for API requests/responses
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models import DeploymentStatus, AgentType


# Generate/Schema Requests
class GenerateRequest(BaseModel):
    """Request to generate agent code"""
    prompt: str = Field(..., description="Natural language prompt describing the agent")
    name: Optional[str] = Field(None, description="Name for the deployment")
    agent_type: Optional[AgentType] = Field(None, description="Agent type if known")
    cloud_provider: Optional[str] = Field("aws", description="Cloud provider")
    scale: Optional[int] = Field(2, description="Number of replicas")
    container_platform: Optional[str] = Field("kubernetes", description="docker or kubernetes")


class GenerateResponse(BaseModel):
    """Response from generation"""
    deployment_id: str
    name: str
    agent_type: str
    files: Dict[str, str]  # File paths and content
    requirements: Dict[str, Any]  # Parsed requirements


# Deployment Requests
class DeployRequest(BaseModel):
    """Request to deploy an agent"""
    deployment_id: Optional[str] = None
    name: str
    agent_type: AgentType
    config: Dict[str, Any]
    generated_files: Dict[str, str]


class DeployResponse(BaseModel):
    """Deployment response"""
    deployment_id: str
    status: DeploymentStatus
    message: str
    endpoints: Optional[Dict[str, str]] = None


# Status/List Responses
class DeploymentStatusResponse(BaseModel):
    """Deployment status response"""
    deployment_id: str
    status: DeploymentStatus
    agent_type: str
    name: str
    created_at: datetime
    replicas: Optional[Dict[str, int]] = None
    endpoints: Optional[Dict[str, str]] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True


class DeploymentListItem(BaseModel):
    """List item for deployments"""
    deployment_id: str
    name: str
    agent_type: str
    status: DeploymentStatus
    created_at: datetime

    class Config:
        from_attributes = True


# Metrics Responses
class MetricResponse(BaseModel):
    """Metrics response"""
    deployment_id: str
    timestamp: datetime
    request_count: int
    success_count: int
    error_count: int
    average_response_time: Optional[float]
    uptime_percentage: Optional[float]
    downtime_minutes: Optional[float]
    is_healthy: bool
    cpu_usage_percent: Optional[float]
    memory_usage_percent: Optional[float]

    class Config:
        from_attributes = True


class KPIResponse(BaseModel):
    """Key Performance Indicators"""
    deployment_id: str
    total_requests: int
    success_rate: float  # percentage
    average_response_time: float
    uptime_percentage: float
    total_downtime_minutes: float
    current_status: str
    health_status: str
    resource_usage: Dict[str, float]


class ProjectCodeResponse(BaseModel):
    """Project code and files response"""
    deployment_id: str
    files: Dict[str, str]  # File paths and content
    file_list: List[str]  # List of file paths
    total_files: int

