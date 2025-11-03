from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from typing import Dict, Any
import os


class TemplateService:
    def __init__(self):
        template_dir = Path(__file__).parent.parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    def render_kubernetes_deployment(self, context: Dict[str, Any]) -> str:
        """Render Kubernetes deployment manifest"""
        template = self.env.from_string(self._get_k8s_deployment_template())
        return template.render(**context)
    
    def render_kubernetes_service(self, context: Dict[str, Any]) -> str:
        """Render Kubernetes service manifest"""
        template = self.env.from_string(self._get_k8s_service_template())
        return template.render(**context)
    
    def render_dockerfile(self, context: Dict[str, Any]) -> str:
        """Render Dockerfile"""
        template = self.env.from_string(self._get_dockerfile_template())
        return template.render(**context)
    
    def render_github_actions(self, context: Dict[str, Any]) -> str:
        """Render GitHub Actions workflow"""
        template = self.env.from_string(self._get_github_actions_template())
        return template.render(**context)
    
    def render_terraform_eks(self, context: Dict[str, Any]) -> str:
        """Render Terraform EKS configuration"""
        template = self.env.from_string(self._get_terraform_eks_template())
        return template.render(**context)
    
    def _get_k8s_deployment_template(self) -> str:
        return """apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ app_name }}
  namespace: {{ namespace }}
  labels:
    app: {{ app_name }}
    version: {{ version }}
spec:
  replicas: {{ replicas }}
  selector:
    matchLabels:
      app: {{ app_name }}
  template:
    metadata:
      labels:
        app: {{ app_name }}
        version: {{ version }}
    spec:
      containers:
      - name: {{ app_name }}
        image: {{ image }}
        ports:
        - containerPort: {{ port }}
        env:
        {% for key, value in env_vars.items() %}
        - name: {{ key }}
          value: "{{ value }}"
        {% endfor %}
        resources:
          requests:
            memory: "{{ memory_request }}"
            cpu: "{{ cpu_request }}"
          limits:
            memory: "{{ memory_limit }}"
            cpu: "{{ cpu_limit }}"
        livenessProbe:
          httpGet:
            path: /health
            port: {{ port }}
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: {{ port }}
          initialDelaySeconds: 5
          periodSeconds: 5
"""
    
    def _get_k8s_service_template(self) -> str:
        return """apiVersion: v1
kind: Service
metadata:
  name: {{ app_name }}-service
  namespace: {{ namespace }}
spec:
  selector:
    app: {{ app_name }}
  ports:
  - protocol: TCP
    port: 80
    targetPort: {{ port }}
  type: {{ service_type }}
"""
    
    def _get_dockerfile_template(self) -> str:
        return """FROM python:3.11-slim as builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH

EXPOSE {{ port }}

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "{{ port }}"]
"""
    
    def _get_github_actions_template(self) -> str:
        return """name: Deploy {{ app_name }}

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: {{ aws_region }}
    
    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v1
    
    - name: Build and push Docker image
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        ECR_REPOSITORY: {{ ecr_repository }}
        IMAGE_TAG: ${{ github.sha }}
      run: |
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
    
    - name: Deploy to EKS
      run: |
        aws eks update-kubeconfig --name {{ cluster_name }} --region {{ aws_region }}
        kubectl set image deployment/{{ app_name }} {{ app_name }}=$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG -n {{ namespace }}
        kubectl rollout status deployment/{{ app_name }} -n {{ namespace }}
"""
    
    def _get_terraform_eks_template(self) -> str:
        return """terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "{{ aws_region }}"
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = "{{ cluster_name }}"
  cluster_version = "1.28"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  eks_managed_node_groups = {
    default = {
      min_size     = {{ min_nodes }}
      max_size     = {{ max_nodes }}
      desired_size = {{ desired_nodes }}

      instance_types = ["{{ instance_type }}"]
    }
  }
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "{{ cluster_name }}-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["{{ aws_region }}a", "{{ aws_region }}b", "{{ aws_region }}c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true
}
"""


template_service = TemplateService()