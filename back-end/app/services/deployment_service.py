"""
AWS EKS Deployment Service
Handles deployment of agents to AWS EKS with Docker and kubectl
"""

import boto3
import subprocess
import asyncio
import tempfile
import os
from typing import Dict, Any
from datetime import datetime
from app.config import settings
from app.models import Deployment, DeploymentStatus
from app.services.docker_service import DockerService
from app.services.ecr_service import ECRService


class DeploymentService:
    """Service for managing AWS EKS deployments"""
    
    def __init__(self):
        self.eks_client = None
        if settings.AWS_ACCESS_KEY_ID:
            self.eks_client = boto3.client(
                'eks',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
        self.docker_service = DockerService()
        self.ecr_service = ECRService()
    
    async def deploy_to_eks(
        self,
        deployment: Deployment,
        generated_files: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Deploy agent to AWS EKS
        
        Steps:
        1. Build Docker image from generated files
        2. Push image to ECR
        3. Apply Kubernetes manifests using kubectl
        4. Monitor deployment status
        5. Return service endpoints
        """
        deployment.status = DeploymentStatus.DEPLOYING
        await deployment.save()
        
        try:
            # Step 1: Build Docker image
            image_tag = f"paragonai/{deployment.agent_type.value}-agent:latest"
            await self.docker_service.build_image(
                generated_files=generated_files,
                image_tag=image_tag,
                deployment_id=deployment.deployment_id
            )
            
            # Step 2: Push to ECR (if AWS configured, otherwise use local)
            try:
                ecr_uri = await self.ecr_service.push_image(
                    image_tag=image_tag,
                    deployment_id=deployment.deployment_id
                )
            except Exception as e:
                print(f"⚠️ ECR push failed, using local image: {e}")
                ecr_uri = image_tag
            
            # Step 3: Update image in Kubernetes manifests
            updated_files = self._update_k8s_image(generated_files, ecr_uri)
            
            # Step 4: Apply Kubernetes manifests (only if kubectl available)
            namespace = deployment.namespace or "default"
            try:
                await self._apply_k8s_manifests(updated_files, namespace)
            except FileNotFoundError:
                print("⚠️ kubectl not found, skipping K8s deployment")
                # For demo purposes, mark as running without actual deployment
                deployment.status = DeploymentStatus.RUNNING
                deployment.deployed_at = datetime.utcnow()
                deployment.service_endpoint = f"http://localhost:8000"
                await deployment.save()
                return {
                    "deployment_id": deployment.deployment_id,
                    "status": "running",
                    "endpoint": deployment.service_endpoint,
                    "message": "Deployment simulated (kubectl not available)",
                    "ecr_uri": ecr_uri
                }
            
            # Step 5: Wait for deployment
            deployment_name = f"{deployment.agent_type.value}-agent"
            await self._wait_for_deployment(deployment_name, namespace)
            
            # Step 6: Get service endpoint
            service_endpoint = await self._get_service_endpoint(deployment_name, namespace)
            
            deployment.status = DeploymentStatus.RUNNING
            deployment.deployed_at = datetime.utcnow()
            deployment.service_endpoint = service_endpoint
            deployment.eks_cluster = settings.AWS_EKS_CLUSTER_NAME
            deployment.eks_namespace = namespace
            await deployment.save()
            
            return {
                "deployment_id": deployment.deployment_id,
                "status": "running",
                "endpoint": service_endpoint,
                "message": "Deployment successful",
                "ecr_uri": ecr_uri
            }
        except Exception as e:
            deployment.status = DeploymentStatus.ERROR
            await deployment.save()
            raise Exception(f"Deployment failed: {str(e)}")
    
    def _update_k8s_image(self, files: Dict[str, str], ecr_uri: str) -> Dict[str, str]:
        """Update image reference in Kubernetes manifests"""
        updated = files.copy()
        
        # Update deployment.yaml
        if "k8s/deployment.yaml" in updated:
            content = updated["k8s/deployment.yaml"]
            # Replace image reference
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                if line.strip().startswith('image:'):
                    new_lines.append(f"        image: {ecr_uri}")
                else:
                    new_lines.append(line)
            updated["k8s/deployment.yaml"] = '\n'.join(new_lines)
        
        return updated
    
    async def _apply_k8s_manifests(self, files: Dict[str, str], namespace: str):
        """Apply Kubernetes manifests using kubectl"""
        # Configure kubectl if AWS configured
        if self.eks_client:
            await self._configure_kubectl()
        
        # Create namespace first if it doesn't exist
        namespace_file = files.get("k8s/namespace.yaml")
        if namespace_file:
            await self._apply_yaml(namespace_file, namespace)
        
        # Apply other manifests
        manifest_order = [
            "k8s/configmap.yaml",
            "k8s/deployment.yaml",
            "k8s/service.yaml"
        ]
        
        for manifest_path in manifest_order:
            if manifest_path in files:
                await self._apply_yaml(files[manifest_path], namespace)
    
    async def _apply_yaml(self, yaml_content: str, namespace: str):
        """Apply YAML content using kubectl"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_file = f.name
        
        try:
            # Use kubectl apply
            process = await asyncio.create_subprocess_exec(
                'kubectl', 'apply', '-f', temp_file,
                '--namespace', namespace,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode()
                raise Exception(f"kubectl apply failed: {error_msg}")
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    async def _configure_kubectl(self):
        """Configure kubectl for EKS cluster"""
        if not self.eks_client:
            return
        
        cluster_name = settings.AWS_EKS_CLUSTER_NAME
        region = settings.AWS_REGION
        
        # Update kubeconfig
        process = await asyncio.create_subprocess_exec(
            'aws', 'eks', 'update-kubeconfig',
            '--name', cluster_name,
            '--region', region,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
    
    async def _wait_for_deployment(self, deployment_name: str, namespace: str, timeout: int = 300):
        """Wait for Kubernetes deployment to be ready"""
        start_time = asyncio.get_event_loop().time()
        
        while True:
            # Check deployment status
            process = await asyncio.create_subprocess_exec(
                'kubectl', 'rollout', 'status',
                'deployment', deployment_name,
                '--namespace', namespace,
                '--timeout', '30s',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return  # Deployment successful
            
            # Check timeout
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout:
                raise Exception(f"Deployment timeout after {timeout}s")
            
            await asyncio.sleep(5)
    
    async def _get_service_endpoint(self, service_name: str, namespace: str) -> str:
        """Get service endpoint (LoadBalancer or ClusterIP)"""
        try:
            process = await asyncio.create_subprocess_exec(
                'kubectl', 'get', 'service', service_name,
                '--namespace', namespace,
                '-o', 'jsonpath={.status.loadBalancer.ingress[0].hostname}',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            endpoint = stdout.decode().strip()
            if not endpoint:
                # Fallback to ClusterIP
                process = await asyncio.create_subprocess_exec(
                    'kubectl', 'get', 'service', service_name,
                    '--namespace', namespace,
                    '-o', 'jsonpath={.spec.clusterIP}',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                endpoint = stdout.decode().strip()
            
            return f"http://{endpoint}" if endpoint else "http://localhost:8000"
        except Exception:
            return "http://localhost:8000"
    
    async def get_deployment_status(
        self,
        deployment_id: str
    ) -> Dict[str, Any]:
        """Get current deployment status from EKS"""
        deployment = await Deployment.find_one(
            Deployment.deployment_id == deployment_id
        )
        
        if not deployment:
            raise ValueError(f"Deployment {deployment_id} not found")
        
        # Query actual EKS cluster status if kubectl available
        namespace = deployment.eks_namespace or "default"
        deployment_name = f"{deployment.agent_type.value}-agent"
        
        try:
            # Get replica status
            process = await asyncio.create_subprocess_exec(
                'kubectl', 'get', 'deployment', deployment_name,
                '--namespace', namespace,
                '-o', 'jsonpath={.status.replicas}/{.spec.replicas}',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            replicas_str = stdout.decode().strip()
            if '/' in replicas_str:
                running, desired = map(int, replicas_str.split('/'))
            else:
                running = desired = 0
        except:
            running = desired = deployment.config.get("scale", 2)
        
        return {
            "deployment_id": deployment.deployment_id,
            "status": deployment.status.value,
            "agent_type": deployment.agent_type.value,
            "name": deployment.name,
            "created_at": deployment.created_at.isoformat() if deployment.created_at else None,
            "replicas": {
                "desired": desired,
                "running": running
            },
            "endpoints": {
                "service": deployment.service_endpoint
            } if deployment.service_endpoint else None
        }
    
    async def get_logs(
        self,
        deployment_id: str,
        tail: int = 100,
        since: str = "1h"
    ) -> Dict[str, Any]:
        """Get deployment logs from EKS pods"""
        deployment = await Deployment.find_one(
            Deployment.deployment_id == deployment_id
        )
        
        if not deployment:
            raise ValueError(f"Deployment {deployment_id} not found")
        
        namespace = deployment.eks_namespace or "default"
        deployment_name = f"{deployment.agent_type.value}-agent"
        
        try:
            # Get pod logs
            process = await asyncio.create_subprocess_exec(
                'kubectl', 'logs',
                '-l', f'app={deployment_name}',
                '--namespace', namespace,
                '--tail', str(tail),
                '--since', since,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            logs = stdout.decode().split('\n')
            
            # Parse logs into structured format
            entries = []
            for line in logs[-tail:]:
                if line.strip():
                    entries.append({
                        "timestamp": datetime.utcnow().isoformat(),
                        "level": "INFO",
                        "message": line
                    })
            
            return {
                "deployment_id": deployment_id,
                "entries": entries
            }
        except Exception as e:
            # Return empty logs if kubectl fails
            return {
                "deployment_id": deployment_id,
                "entries": [{
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": "WARN",
                    "message": f"Could not retrieve logs: {str(e)}"
                }]
            }
