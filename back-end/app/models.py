from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class Generation(BaseModel):
    id: str = Field(alias="_id")
    prompt: str
    agent_type: str
    cloud_provider: str
    status: str
    files_generated: List[str] = []
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


class Deployment(BaseModel):
    id: str = Field(alias="_id")
    generation_id: str
    agent_type: str
    cloud_provider: str
    cluster_name: Optional[str] = None
    namespace: str
    status: str
    endpoint: Optional[str] = None
    dashboard_url: Optional[str] = None
    replicas: int
    version: str = "v1"
    previous_versions: List[str] = []
    config: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


class Metrics(BaseModel):
    id: str = Field(alias="_id")
    deployment_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_count: int = 0
    error_count: int = 0
    total_response_time: float = 0.0
    avg_response_time: float = 0.0
    uptime_seconds: int = 0
    
    class Config:
        populate_by_name = True