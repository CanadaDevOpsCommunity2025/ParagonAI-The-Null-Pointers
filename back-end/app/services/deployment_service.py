from pathlib import Path
from typing import Dict, Any, Optional
import uuid
import shutil
import logging
from datetime import datetime

from app.services.llm_service import llm_service
from app.services.template_service import template_service
from app.services.docker_service import docker_service
from app.services.kubernetes_service import kubernetes_service
from app.services.terraform_service import terraform_service
from app.services.cicd_service import cicd_service
from app.services.monitoring_service import monitoring_service
from app.schemas import AgentType, CloudProvider, DeploymentStatus

logger = logging.getLogger(__name__)


class DeploymentService:
    def __init__(self):
        self.output_base_dir = Path("/tmp/paragon_generations")
        self.output_base_dir.mkdir(exist_ok=True)
    
    def generate_full_deployment(self, prompt: str, agent_type: Optional[AgentType], 
                                cloud_provider: CloudProvider, enable_monitoring: bool,
                                enable_cicd: bool, enable_security_scan: bool) -> Dict[str, Any]:
        """Generate complete deployment package from prompt"""
        generation_id = str(uuid.uuid4())
        output_dir = self.output_base_dir / generation_id
        output_dir.mkdir(exist_ok=True)
        
        try:
            # Parse prompt using LLM
            logger.info(f"Parsing deployment prompt for generation {generation_id}")
            parsed_requirements = llm_service.parse_deployment_prompt(prompt)
            
            # Override with explicit parameters if provided
            if agent_type:
                parsed_requirements["agent_type"] = agent_type.value
            parsed_requirements["cloud_provider"] = cloud_provider.value
            
            app_name = f"{parsed_requirements['agent_type']}-agent"
            
            # Generate agent code
            logger.info("Generating agent code")
            agent_code = llm_service.generate_agent_code(
                parsed_requirements["agent_type"],
                parsed_requirements
            )
            
            # Write agent code
            (output_dir / "main.py").write_text(agent_code)
            
            # Generate requirements.txt
            requirements = self._generate_requirements(parsed_requirements["agent_type"])
            (output_dir / "requirements.txt").write_text(requirements)
            
            # Generate Dockerfile
            logger.info("Generating Dockerfile")
            dockerfile_context = {
                "port": 8000,
                "app_name": app_name
            }
            dockerfile = template_service.render_dockerfile(dockerfile_context)
            (output_dir / "Dockerfile").write_text(dockerfile)
            
            # Generate Kubernetes manifests
            logger.info("Generating Kubernetes manifests")
            k8s_dir = output_dir / "kubernetes"
            k8s_dir.mkdir(exist_ok=True)
            
            k8s_context = {
                "app_name": app_name,
                "namespace": "default",
                "version": "v1",
                "replicas": parsed_requirements.get("scale_requirements", {}).get("replicas", 1),
                "image": f"<registry>/{app_name}:latest",
                "port": 8000,
                "env_vars": {},
                "memory_request": "256Mi",
                "cpu_request": "100m",
                "memory_limit": "512Mi",
                "cpu_limit": "500m",
                "service_type": "LoadBalancer"
            }
            
            deployment_yaml = template_service.render_kubernetes_deployment(k8s_context)
            (k8s_dir / "deployment.yaml").write_text(deployment_yaml)
            
            service_yaml = template_service.render_kubernetes_service(k8s_context)
            (k8s_dir / "service.yaml").write_text(service_yaml)
            
            # Generate Terraform if AWS
            if cloud_provider == CloudProvider.AWS:
                logger.info("Generating Terraform configuration")
                terraform_dir = output_dir / "terraform"
                terraform_dir.mkdir(exist_ok=True)
                
                terraform_context = {
                    "cluster_name": f"{app_name}-cluster",
                    "aws_region": "us-east-1",
                    "min_nodes": 1,
                    "max_nodes": 5,
                    "desired_nodes": 2,
                    "instance_type": "t3.medium"
                }
                
                terraform_config = template_service.render_terraform_eks(terraform_context)
                (terraform_dir / "main.tf").write_text(terraform_config)
            
            # Generate CI/CD pipeline
            if enable_cicd:
                logger.info("Generating CI/CD pipeline")
                cicd_dir = output_dir / ".github" / "workflows"
                cicd_dir.mkdir(parents=True, exist_ok=True)
                
                cicd_context = {
                    "app_name": app_name,
                    "aws_region": "us-east-1",
                    "ecr_repository": app_name,
                    "cluster_name": f"{app_name}-cluster",
                    "namespace": "default"
                }
                
                github_workflow = cicd_service.generate_github_actions(cicd_context)
                (cicd_dir / "deploy.yml").write_text(github_workflow)
            
            # Generate monitoring configs
            if enable_monitoring:
                logger.info("Generating monitoring configuration")
                monitoring_dir = output_dir / "monitoring"
                monitoring_dir.mkdir(exist_ok=True)
                
                monitoring_context = {
                    "app_name": app_name,
                    "namespace": "default"
                }
                
                prometheus_config = monitoring_service.generate_prometheus_config(monitoring_context)
                (monitoring_dir / "prometheus.yaml").write_text(prometheus_config)
                
                grafana_config = monitoring_service.generate_grafana_config(monitoring_context)
                (monitoring_dir / "grafana.yaml").write_text(grafana_config)
                
                dashboard = monitoring_service.generate_grafana_dashboard(monitoring_context)
                (monitoring_dir / "dashboard.json").write_text(dashboard)
            
            # Generate README
            readme = self._generate_readme(app_name, parsed_requirements, cloud_provider)
            (output_dir / "README.md").write_text(readme)
            
            # List all generated files
            files_generated = [str(f.relative_to(output_dir)) for f in output_dir.rglob("*") if f.is_file()]
            
            logger.info(f"Generation complete: {len(files_generated)} files created")
            
            return {
                "generation_id": generation_id,
                "status": "success",
                "output_path": str(output_dir),
                "files_generated": files_generated,
                "parsed_requirements": parsed_requirements
            }
        
        except Exception as e:
            logger.error(f"Generation failed: {e}", exc_info=True)
            return {
                "generation_id": generation_id,
                "status": "failed",
                "error": str(e),
                "files_generated": []
            }
    
    def deploy_to_kubernetes(self, generation_id: str, namespace: str, 
                            replicas: int) -> Dict[str, Any]:
        """Deploy generated application to Kubernetes"""
        output_dir = self.output_base_dir / generation_id
        
        if not output_dir.exists():
            return {"status": "failed", "error": "Generation not found"}
        
        try:
            # Create namespace
            kubernetes_service.create_namespace(namespace)
            
            # Apply Kubernetes manifests
            k8s_dir = output_dir / "kubernetes"
            for manifest in k8s_dir.glob("*.yaml"):
                success = kubernetes_service.apply_manifest(str(manifest))
                if not success:
                    return {"status": "failed", "error": f"Failed to apply {manifest.name}"}
            
            # Get deployment status
            app_name = self._extract_app_name(output_dir)
            status = kubernetes_service.get_deployment_status(app_name, namespace)
            endpoint = kubernetes_service.get_service_endpoint(f"{app_name}-service", namespace)
            
            return {
                "status": "deployed" if status.get("ready") else "deploying",
                "deployment_status": status,
                "endpoint": endpoint
            }
        
        except Exception as e:
            logger.error(f"Deployment failed: {e}", exc_info=True)
            return {"status": "failed", "error": str(e)}
    
    def _generate_requirements(self, agent_type: str) -> str:
        """Generate requirements.txt based on agent type"""
        base_requirements = [
            "fastapi==0.120.4",
            "uvicorn==0.34.0",
            "pydantic==2.10.5",
            "python-dotenv==1.2.1",
            "openai==2.6.1"
        ]
        
        if agent_type == "customer_support":
            base_requirements.extend([
                "langchain==0.3.15",
                "langchain-openai==0.3.0"
            ])
        elif agent_type == "content_writer":
            base_requirements.extend([
                "crewai==0.95.0"
            ])
        elif agent_type == "data_analyst":
            base_requirements.extend([
                "pyautogen==0.4.0",
                "pandas==2.2.3"
            ])
        
        return "\n".join(base_requirements)
    
    def _generate_readme(self, app_name: str, requirements: Dict[str, Any], 
                        cloud_provider: CloudProvider) -> str:
        """Generate README documentation"""
        return f"""# {app_name}

Generated AI Agent Deployment

## Overview

- **Agent Type**: {requirements.get('agent_type', 'N/A')}
- **Cloud Provider**: {cloud_provider.value}
- **Generated**: {datetime.utcnow().isoformat()}

## Deployment Instructions

### Prerequisites

- Docker installed
- kubectl configured
- {cloud_provider.value.upper()} credentials configured

### Quick Start

1. **Build Docker Image**
   ```bash
   docker build -t {app_name}:latest .
   ```

2. **Deploy to Kubernetes**
   ```bash
   kubectl apply -f kubernetes/
   ```

3. **Check Status**
   ```bash
   kubectl get pods
   kubectl get services
   ```

### Monitoring

If monitoring is enabled, access dashboards:

- **Prometheus**: `kubectl port-forward svc/prometheus 9090:9090`
- **Grafana**: `kubectl port-forward svc/grafana 3000:3000`

### CI/CD

GitHub Actions workflow is configured in `.github/workflows/deploy.yml`

Required secrets:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

## API Endpoints

- `GET /health` - Health check
- `POST /chat` - Chat with agent

## Support

Generated by ParagonAI Platform
"""
    
    def _extract_app_name(self, output_dir: Path) -> str:
        """Extract app name from generated files"""
        deployment_file = output_dir / "kubernetes" / "deployment.yaml"
        if deployment_file.exists():
            import yaml
            with open(deployment_file) as f:
                deployment = yaml.safe_load(f)
                return deployment["metadata"]["name"]
        return "agent-app"


deployment_service = DeploymentService()