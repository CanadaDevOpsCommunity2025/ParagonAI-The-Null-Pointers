from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "ParagonAI Agent Deployment Platform"
    VERSION: str = "1.0.0"
    
    # LLM Settings
    GROQ_API_KEY: str
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    DEFAULT_LLM_PROVIDER: str = "groq"
    DEFAULT_MODEL: str = "openai/gpt-oss-120b"
    
    # MongoDB Settings
    MONGODB_URL: str = "mongodb://mongodb:27017"
    MONGODB_DB: str = "paragonai"
    MONGODB_DB_NAME: Optional[str] = None  # For backward compatibility
    
    # Docker Settings
    DOCKER_REGISTRY: str = "docker.io"
    DOCKER_USERNAME: Optional[str] = None
    DOCKER_PASSWORD: Optional[str] = None
    
    # AWS Settings
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    ECR_REGISTRY: Optional[str] = None
    
    # Azure Settings
    AZURE_SUBSCRIPTION_ID: Optional[str] = None
    AZURE_TENANT_ID: Optional[str] = None
    AZURE_CLIENT_ID: Optional[str] = None
    AZURE_CLIENT_SECRET: Optional[str] = None
    
    # GCP Settings
    GCP_PROJECT_ID: Optional[str] = None
    GCP_SERVICE_ACCOUNT_KEY: Optional[str] = None
    
    # Kubernetes Settings
    KUBECONFIG_PATH: Optional[str] = None
    DEFAULT_NAMESPACE: str = "default"
    
    # Security Settings
    ENABLE_SECURITY_SCAN: bool = True
    TRIVY_ENABLED: bool = True
    
    # Monitoring Settings
    PROMETHEUS_ENABLED: bool = True
    GRAFANA_ENABLED: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()