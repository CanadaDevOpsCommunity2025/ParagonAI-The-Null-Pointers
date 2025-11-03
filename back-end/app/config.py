# app/config.py
from pydantic_settings import BaseSettings
from typing import List, Optional, Any, Dict
import secrets
from datetime import timedelta

class SecuritySettings(BaseSettings):
    """Security related settings"""
    SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    RATE_LIMIT: str = "100/minute"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

class AwsSettings(BaseSettings):
    """AWS related settings"""
    ACCESS_KEY_ID: str = ""
    SECRET_ACCESS_KEY: str = ""
    REGION: str = "us-east-1"
    EKS_CLUSTER_NAME: str = "paragonai-cluster"
    ECR_REGISTRY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

class DatabaseSettings(BaseSettings):
    """Database settings"""
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "paragonai"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

class AppSettings(BaseSettings):
    """Main application settings"""
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    OPENAI_API_KEY: str = ""
    
    # Initialize other settings
    security: SecuritySettings = SecuritySettings()
    aws: AwsSettings = AwsSettings()
    db: DatabaseSettings = DatabaseSettings()
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        env_nested_delimiter = "__"

# Create settings instance
settings = AppSettings()