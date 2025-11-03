from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum


class AgentType(str, Enum):
    CUSTOMER_SUPPORT = "customer_support"
    CONTENT_WRITER = "content_writer"
    DATA_ANALYST = "data_analyst"


class CloudProvider(str, Enum):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    ONPREM = "onprem"


class DeploymentStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    BUILDING = "building"
    DEPLOYING = "deploying"
    RUNNING = "running"
    FAILED = "failed"
    STOPPED = "stopped"


class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="Natural language description of the agent to deploy")
    agent_type: Optional[AgentType] = None
    cloud_provider: CloudProvider = CloudProvider.AWS
    enable_monitoring: bool = True
    enable_cicd: bool = True
    enable_security_scan: bool = True


class GenerateResponse(BaseModel):
    generation_id: str
    status: str
    message: str
    files_generated: List[str]
    download_url: Optional[str] = None


class AgentDefaultConfig(BaseModel):
    model: str = "mixtral-8x7b-32768"
    temperature: float = 0.1
    max_tokens: int = 4096
    system_prompt: str = "You are a helpful AI assistant."

class AgentTemplate(BaseModel):
    id: str
    name: str
    description: str
    agent_type: AgentType
    framework: str
    use_cases: List[str]
    default_config: AgentDefaultConfig


class DeploymentRequest(BaseModel):
    generation_id: str
    cloud_provider: CloudProvider
    cluster_name: Optional[str] = None
    namespace: str = "default"
    replicas: int = 1
    auto_scale: bool = False
    min_replicas: int = 1
    max_replicas: int = 10


class DeploymentResponse(BaseModel):
    deployment_id: str
    status: DeploymentStatus
    message: str
    endpoint: Optional[str] = None
    dashboard_url: Optional[str] = None


class DeploymentInfo(BaseModel):
    deployment_id: str
    generation_id: str
    agent_type: AgentType
    cloud_provider: CloudProvider
    status: DeploymentStatus
    endpoint: Optional[str] = None
    dashboard_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    metrics: Optional[Dict[str, Any]] = None


class MetricsResponse(BaseModel):
    deployment_id: str
    request_count: int
    error_count: int
    avg_response_time: float
    uptime_percentage: float
    last_updated: datetime


class RollbackRequest(BaseModel):
    deployment_id: str
    target_version: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime