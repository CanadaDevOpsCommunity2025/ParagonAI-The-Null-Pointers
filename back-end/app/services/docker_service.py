import docker
import subprocess
from pathlib import Path
from typing import Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class DockerService:
    def __init__(self):
        try:
            self.client = docker.from_env()
        except Exception as e:
            logger.warning(f"Docker client initialization failed: {e}")
            self.client = None
    
    def build_image(self, context_path: str, image_name: str, tag: str = "latest") -> bool:
        """Build Docker image from context path"""
        try:
            full_tag = f"{image_name}:{tag}"
            logger.info(f"Building image: {full_tag}")
            
            if self.client:
                image, logs = self.client.images.build(
                    path=context_path,
                    tag=full_tag,
                    rm=True,
                    forcerm=True
                )
                for log in logs:
                    if 'stream' in log:
                        logger.debug(log['stream'].strip())
                return True
            else:
                result = subprocess.run(
                    ["docker", "build", "-t", full_tag, context_path],
                    capture_output=True,
                    text=True
                )
                return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to build image: {e}")
            return False
    
    def push_image(self, image_name: str, tag: str = "latest", registry: Optional[str] = None) -> bool:
        """Push image to registry"""
        try:
            if registry:
                full_name = f"{registry}/{image_name}:{tag}"
            else:
                full_name = f"{image_name}:{tag}"
            
            logger.info(f"Pushing image: {full_name}")
            
            if self.client:
                for line in self.client.images.push(full_name, stream=True, decode=True):
                    if 'status' in line:
                        logger.debug(line['status'])
                return True
            else:
                result = subprocess.run(
                    ["docker", "push", full_name],
                    capture_output=True,
                    text=True
                )
                return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to push image: {e}")
            return False
    
    def tag_image(self, source: str, target: str) -> bool:
        """Tag an image"""
        try:
            if self.client:
                image = self.client.images.get(source)
                image.tag(target)
                return True
            else:
                result = subprocess.run(
                    ["docker", "tag", source, target],
                    capture_output=True,
                    text=True
                )
                return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to tag image: {e}")
            return False
    
    def login(self, registry: str, username: str, password: str) -> bool:
        """Login to Docker registry"""
        try:
            if self.client:
                self.client.login(username=username, password=password, registry=registry)
                return True
            else:
                result = subprocess.run(
                    ["docker", "login", "-u", username, "-p", password, registry],
                    capture_output=True,
                    text=True
                )
                return result.returncode == 0
        except Exception as e:
            logger.error(f"Failed to login to registry: {e}")
            return False
    
    def scan_image(self, image_name: str, tag: str = "latest") -> dict:
        """Scan image for vulnerabilities using Trivy"""
        if not settings.TRIVY_ENABLED:
            return {"vulnerabilities": [], "scan_enabled": False}
        
        try:
            full_name = f"{image_name}:{tag}"
            result = subprocess.run(
                ["trivy", "image", "--format", "json", full_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                import json
                return json.loads(result.stdout)
            else:
                logger.warning("Trivy scan failed or not installed")
                return {"vulnerabilities": [], "scan_enabled": False}
        except FileNotFoundError:
            logger.warning("Trivy not installed")
            return {"vulnerabilities": [], "scan_enabled": False}
        except Exception as e:
            logger.error(f"Failed to scan image: {e}")
            return {"vulnerabilities": [], "error": str(e)}


docker_service = DockerService()