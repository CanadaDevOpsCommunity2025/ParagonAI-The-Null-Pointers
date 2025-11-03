"""
Advanced Prompt Engineering for Code Generation
Uses OpenAI to generate deployment infrastructure code
"""

import os
import json
from typing import Dict, Any, List
from openai import OpenAI
from app.config import settings


class PromptEngineer:
    """Advanced prompt engineering for generating infrastructure code"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
    
    def generate_infrastructure_code(
        self, 
        prompt: str, 
        agent_type: str,
        requirements: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Generate complete infrastructure code using advanced prompt engineering
        """
        if not self.client:
            raise ValueError("OpenAI API key not configured")
        
        system_prompt = self._build_system_prompt(agent_type, requirements)
        user_prompt = self._build_user_prompt(prompt, requirements)
        
        # Generate all files in parallel for efficiency
        files = {}
        
        # Core agent file
        files["agent.py"] = self._generate_agent_code(agent_type, prompt, requirements)
        
        # Infrastructure files
        files["Dockerfile"] = self._generate_dockerfile(agent_type, requirements)
        files["requirements.txt"] = self._generate_requirements(agent_type, requirements)
        
        # Kubernetes files
        if requirements.get("container_platform") in ["kubernetes", "both"]:
            files.update(self._generate_kubernetes_files(agent_type, requirements))
        
        # Docker Compose
        if requirements.get("container_platform") in ["docker", "both"]:
            files["docker-compose.yml"] = self._generate_docker_compose(agent_type, requirements)
        
        # CI/CD
        files[".github/workflows/deploy.yml"] = self._generate_cicd_pipeline(agent_type, requirements)
        
        # AWS EKS specific
        if requirements.get("cloud_provider") == "aws":
            files.update(self._generate_aws_files(agent_type, requirements))
        
        # README
        files["README.md"] = self._generate_readme(agent_type, requirements)
        
        return files
    
    def _build_system_prompt(self, agent_type: str, requirements: Dict[str, Any]) -> str:
        """Build system prompt for code generation"""
        return f"""You are an expert DevOps engineer specializing in AI agent deployment on AWS EKS.
Your task is to generate production-ready infrastructure code.

Agent Type: {agent_type}
Deployment Platform: {requirements.get('cloud_provider', 'aws')} EKS
Replicas: {requirements.get('scale', 2)}

Guidelines:
1. Generate production-ready, secure code
2. Include proper error handling and logging
3. Use best practices for containerization
4. Include health checks and monitoring
5. Optimize for AWS EKS deployment
6. Include proper resource limits
7. Use environment variables for configuration
8. Include proper security contexts
"""
    
    def _build_user_prompt(self, prompt: str, requirements: Dict[str, Any]) -> str:
        """Build user prompt with context"""
        context = f"""
User Request: {prompt}

Generate the following files for AWS EKS deployment:
1. Python agent code with FastAPI
2. Dockerfile optimized for production
3. Kubernetes Deployment manifest
4. Kubernetes Service manifest
5. Kubernetes ConfigMap
6. Kubernetes Secrets template
7. AWS EKS deployment configuration
8. CI/CD pipeline for automated deployment
9. Monitoring and health check configurations

Requirements:
- Cloud: AWS EKS
- Replicas: {requirements.get('scale', 2)}
- Agent Type: {requirements.get('agent_type', 'customer_support')}
- Include proper logging and metrics collection
"""
        return context
    
    def _generate_with_llm(self, prompt: str, max_tokens: int = 2000) -> str:
        """Generate code using LLM"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert DevOps engineer. Generate production-ready code."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating with LLM: {e}")
            return ""
    
    def _generate_agent_code(self, agent_type: str, prompt: str, requirements: Dict[str, Any]) -> str:
        """Generate agent Python code"""
        from app.templates import get_agent_template
        base_code = get_agent_template(agent_type)
        
        # Enhance with LLM if needed
        enhancement_prompt = f"""
Enhance this agent code based on the user request: {prompt}

Current code:
{base_code}

Add:
1. FastAPI endpoints for health checks
2. Metrics collection
3. Proper error handling
4. Request/response logging
5. Environment variable configuration

Generate only the complete Python code, no explanations.
"""
        enhanced_code = self._generate_with_llm(enhancement_prompt, max_tokens=3000)
        return enhanced_code if enhanced_code else base_code
    
    def _generate_dockerfile(self, agent_type: str, requirements: Dict[str, Any]) -> str:
        """Generate optimized Dockerfile"""
        prompt = f"""
Generate a production-ready Dockerfile for a {agent_type} AI agent.

Requirements:
- Use Python 3.11-slim base image
- Install dependencies from requirements.txt
- Expose port 8000
- Include health check
- Optimize for smaller image size
- Use non-root user
- Include proper labels

Generate only the Dockerfile content.
"""
        dockerfile = self._generate_with_llm(prompt)
        if not dockerfile:
            # Fallback template
            dockerfile = f"""FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent.py .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "agent:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        return dockerfile
    
    def _generate_requirements(self, agent_type: str, requirements: Dict[str, Any]) -> str:
        """Generate requirements.txt"""
        from app.templates import get_requirements_template
        return get_requirements_template(agent_type)
    
    def _generate_kubernetes_files(self, agent_type: str, requirements: Dict[str, Any]) -> Dict[str, str]:
        """Generate Kubernetes manifest files"""
        replicas = requirements.get('scale', 2)
        namespace = requirements.get('namespace', 'default')
        
        deployment_prompt = f"""
Generate Kubernetes Deployment manifest for {agent_type} agent.

Requirements:
- Name: {agent_type}-agent
- Replicas: {replicas}
- Namespace: {namespace}
- Image: paragonai/{agent_type}-agent:latest
- Port: 8000
- Resource limits: CPU 500m, Memory 512Mi
- Resource requests: CPU 250m, Memory 256Mi
- Health checks (liveness and readiness)
- Environment variables from ConfigMap and Secrets
- AWS EKS optimized

Generate only the YAML content.
"""
        
        service_prompt = f"""
Generate Kubernetes Service manifest for {agent_type} agent.

- Name: {agent_type}-service
- Type: LoadBalancer (for AWS ELB)
- Port: 80 -> 8000
- Selector: app={agent_type}-agent

Generate only the YAML content.
"""
        
        configmap_prompt = f"""
Generate Kubernetes ConfigMap for {agent_type} agent.

Include:
- Redis URL
- Agent type
- Log level
- Environment

Generate only the YAML content.
"""
        
        files = {
            "k8s/deployment.yaml": self._generate_with_llm(deployment_prompt) or self._k8s_deployment_template(agent_type, replicas, namespace),
            "k8s/service.yaml": self._generate_with_llm(service_prompt) or self._k8s_service_template(agent_type),
            "k8s/configmap.yaml": self._generate_with_llm(configmap_prompt) or self._k8s_configmap_template(agent_type),
            "k8s/namespace.yaml": self._k8s_namespace_template(namespace)
        }
        
        return files
    
    def _generate_docker_compose(self, agent_type: str, requirements: Dict[str, Any]) -> str:
        """Generate docker-compose.yml"""
        return f"""version: '3.8'

services:
  {agent_type}-agent:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${{OPENAI_API_KEY}}
    depends_on:
      - redis
    restart: unless-stopped
    networks:
      - paragonai-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - paragonai-network

volumes:
  redis-data:

networks:
  paragonai-network:
    driver: bridge
"""
    
    def _generate_cicd_pipeline(self, agent_type: str, requirements: Dict[str, Any]) -> str:
        """Generate CI/CD pipeline"""
        return f"""name: Deploy {agent_type} Agent to AWS EKS

on:
  push:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{{{ secrets.AWS_ACCESS_KEY_ID }}}}
        aws-secret-access-key: ${{{{ secrets.AWS_SECRET_ACCESS_KEY }}}}
        aws-region: {requirements.get('region', 'us-east-1')}
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Amazon ECR
      uses: aws-actions/amazon-ecr-login@v1
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: ${{{{ secrets.ECR_REGISTRY }}}}/paragonai/{agent_type}-agent:latest
    
    - name: Security scan with Trivy
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: ${{{{ secrets.ECR_REGISTRY }}}}/paragonai/{agent_type}-agent:latest
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Configure kubectl
      run: |
        aws eks update-kubeconfig --name ${{{{ secrets.EKS_CLUSTER_NAME }}}}
    
    - name: Deploy to EKS
      run: |
        kubectl apply -f k8s/namespace.yaml
        kubectl apply -f k8s/configmap.yaml
        kubectl apply -f k8s/deployment.yaml
        kubectl apply -f k8s/service.yaml
        kubectl rollout status deployment/{agent_type}-agent -n {requirements.get('namespace', 'default')}
"""
    
    def _generate_aws_files(self, agent_type: str, requirements: Dict[str, Any]) -> Dict[str, str]:
        """Generate AWS-specific configuration files"""
        return {
            "aws/eks-config.yaml": f"""# AWS EKS Configuration
clusterName: {requirements.get('cluster_name', 'paragonai-cluster')}
region: {requirements.get('region', 'us-east-1')}
namespace: {requirements.get('namespace', 'default')}
serviceAccount: {agent_type}-service-account
""",
            "aws/iam-policy.json": """{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "eks:DescribeCluster",
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage"
      ],
      "Resource": "*"
    }
  ]
}
"""
        }
    
    def _generate_readme(self, agent_type: str, requirements: Dict[str, Any]) -> str:
        """Generate README"""
        return f"""# {agent_type.replace('_', ' ').title()} Agent

Generated deployment package for AWS EKS.

## Deployment

### Prerequisites
- AWS CLI configured
- kubectl configured
- Access to EKS cluster

### Deploy to EKS

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

## Configuration

- Replicas: {requirements.get('scale', 2)}
- Region: {requirements.get('region', 'us-east-1')}
- Namespace: {requirements.get('namespace', 'default')}
"""
    
    # Template methods for fallback
    def _k8s_deployment_template(self, agent_type: str, replicas: int, namespace: str) -> str:
        """Kubernetes deployment template"""
        return f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {agent_type}-agent
  namespace: {namespace}
  labels:
    app: {agent_type}-agent
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      app: {agent_type}-agent
  template:
    metadata:
      labels:
        app: {agent_type}-agent
    spec:
      containers:
      - name: agent
        image: paragonai/{agent_type}-agent:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: {agent_type}-config
              key: redis_url
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: agent-secrets
              key: openai_api_key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
"""
    
    def _k8s_service_template(self, agent_type: str) -> str:
        """Kubernetes service template"""
        return f"""apiVersion: v1
kind: Service
metadata:
  name: {agent_type}-service
spec:
  selector:
    app: {agent_type}-agent
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
"""
    
    def _k8s_configmap_template(self, agent_type: str) -> str:
        """Kubernetes ConfigMap template"""
        return f"""apiVersion: v1
kind: ConfigMap
metadata:
  name: {agent_type}-config
data:
  redis_url: "redis://redis-service:6379"
  agent_type: "{agent_type}"
  log_level: "INFO"
"""
    
    def _k8s_namespace_template(self, namespace: str) -> str:
        """Kubernetes namespace template"""
        return f"""apiVersion: v1
kind: Namespace
metadata:
  name: {namespace}
"""

