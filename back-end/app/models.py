"""
MongoDB document models using Beanie ODM
"""

from beanie import Document
from pydantic import Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class DeploymentStatus(str, Enum):
    """Deployment status enum"""
    PENDING = "pending"
    DEPLOYING = "deploying"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    FAILED = "failed"


class AgentType(str, Enum):
    """Agent type enum"""
    CUSTOMER_SUPPORT = "customer_support"
    CONTENT_WRITER = "content_writer"
    DATA_ANALYST = "data_analyst"


class Deployment(Document):
    """Deployment document model"""
    
    deployment_id: str = Field(..., unique=True, index=True)
    name: str
    agent_type: AgentType
    
    # Configuration
    config: Dict[str, Any] = Field(default_factory=dict)
    prompt: Optional[str] = None
    
    # Generated files metadata
    generated_files: Dict[str, str] = Field(default_factory=dict)
    
    # Deployment info
    status: DeploymentStatus = DeploymentStatus.PENDING
    cloud_provider: str = "aws"
    region: Optional[str] = None
    cluster_name: Optional[str] = None
    namespace: Optional[str] = None
    
    # AWS/EKS specific
    eks_cluster: Optional[str] = None
    eks_namespace: Optional[str] = None
    service_endpoint: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    deployed_at: Optional[datetime] = None
    
    class Settings:
        name = "deployments"
        indexes = [
            "deployment_id",
            "status",
            "agent_type",
            "created_at"
        ]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Metric(Document):
    """Metrics document model for tracking agent performance"""
    
    deployment_id: str = Field(..., index=True)
    
    # Performance metrics
    request_count: int = 0
    success_count: int = 0
    error_count: int = 0
    average_response_time: Optional[float] = None  # in milliseconds
    p50_response_time: Optional[float] = None
    p95_response_time: Optional[float] = None
    p99_response_time: Optional[float] = None
    
    # Availability metrics
    uptime_percentage: Optional[float] = None  # 0-100
    downtime_minutes: Optional[float] = None
    last_health_check: Optional[datetime] = None
    is_healthy: bool = True
    
    # Resource metrics
    cpu_usage_percent: Optional[float] = None
    memory_usage_percent: Optional[float] = None
    pod_count: Optional[int] = None
    replica_count: Optional[int] = None
    
    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "metrics"
        indexes = [
            "deployment_id",
            "timestamp",
            ("deployment_id", "timestamp")
        ]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
