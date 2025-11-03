"""
ECR Service - Push Docker images to AWS ECR
"""

import boto3
import asyncio
import subprocess
from app.config import settings


class ECRService:
    """Service for pushing images to AWS ECR"""
    
    def __init__(self):
        self.ecr_client = boto3.client(
            'ecr',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        ) if settings.AWS_ACCESS_KEY_ID else None
    
    async def push_image(
        self,
        image_tag: str,
        deployment_id: str
    ) -> str:
        """
        Push Docker image to ECR
        
        Args:
            image_tag: Local Docker image tag
            deployment_id: Deployment ID
        
        Returns:
            ECR image URI
        """
        if not self.ecr_client:
            # Return local tag if ECR not configured
            return image_tag
        
        # Get or create ECR repository
        repo_name = image_tag.split(':')[0]  # e.g., paragonai/customer-support-agent
        ecr_uri = await self._get_or_create_repo(repo_name)
        
        # Login to ECR
        await self._ecr_login()
        
        # Tag image with ECR URI
        await self._tag_for_ecr(image_tag, ecr_uri)
        
        # Push image
        await self._push_to_ecr(ecr_uri)
        
        return ecr_uri
    
    async def _get_or_create_repo(self, repo_name: str) -> str:
        """Get or create ECR repository"""
        if not self.ecr_client:
            raise Exception("ECR client not initialized. Check AWS credentials.")
        
        # Get AWS account ID
        sts_client = boto3.client(
            'sts',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        account_id = sts_client.get_caller_identity()['Account']
        region = settings.AWS_REGION
        
        ecr_uri = f"{account_id}.dkr.ecr.{region}.amazonaws.com/{repo_name}"
        
        try:
            # Try to describe repository
            self.ecr_client.describe_repositories(repositoryNames=[repo_name])
        except self.ecr_client.exceptions.RepositoryNotFoundException:
            # Create repository
            self.ecr_client.create_repository(
                repositoryName=repo_name,
                imageTagMutability='MUTABLE',
                imageScanningConfiguration={
                    'scanOnPush': True
                }
            )
        
        return ecr_uri
    
    async def _ecr_login(self):
        """Login to ECR"""
        if not self.ecr_client:
            raise Exception("ECR client not initialized")
        
        region = settings.AWS_REGION
        
        # Get AWS account ID
        sts_client = boto3.client(
            'sts',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=region
        )
        account_id = sts_client.get_caller_identity()['Account']
        
        # Get login token
        token = self.ecr_client.get_authorization_token()['authorizationData'][0]['authorizationToken']
        
        # Login with docker
        registry = f"{account_id}.dkr.ecr.{region}.amazonaws.com"
        login_cmd = f"echo {token} | docker login --username AWS --password-stdin {registry}"
        
        process = await asyncio.create_subprocess_shell(
            login_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode()
            raise Exception(f"Failed to login to ECR: {error_msg}")
    
    async def _tag_for_ecr(self, local_tag: str, ecr_uri: str):
        """Tag image for ECR"""
        process = await asyncio.create_subprocess_exec(
            'docker', 'tag', local_tag, ecr_uri,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        
        if process.returncode != 0:
            raise Exception("Failed to tag image for ECR")
    
    async def _push_to_ecr(self, ecr_uri: str):
        """Push image to ECR"""
        process = await asyncio.create_subprocess_exec(
            'docker', 'push', ecr_uri,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode()
            raise Exception(f"Failed to push image to ECR: {error_msg}")
        
        print(f"✅ Image pushed to ECR: {ecr_uri}")

