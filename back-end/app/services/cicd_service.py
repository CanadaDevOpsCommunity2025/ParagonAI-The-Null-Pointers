from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class CICDService:
    def generate_github_actions(self, config: Dict[str, Any]) -> str:
        """Generate GitHub Actions workflow"""
        app_name = config.get("app_name", "agent-app")
        aws_region = config.get("aws_region", "us-east-1")
        ecr_repository = config.get("ecr_repository", app_name)
        cluster_name = config.get("cluster_name", "agent-cluster")
        namespace = config.get("namespace", "default")
        
        workflow = f"""name: Deploy {app_name}

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  AWS_REGION: {aws_region}
  ECR_REPOSITORY: {ecr_repository}
  EKS_CLUSTER: {cluster_name}
  NAMESPACE: {namespace}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest
    
    - name: Run tests
      run: pytest tests/ -v

  security-scan:
    runs-on: ubuntu-latest
    needs: test
    steps:
    - uses: actions/checkout@v3
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Upload Trivy results to GitHub Security
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'

  build-and-deploy:
    runs-on: ubuntu-latest
    needs: [test, security-scan]
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{{{ secrets.AWS_ACCESS_KEY_ID }}}}
        aws-secret-access-key: ${{{{ secrets.AWS_SECRET_ACCESS_KEY }}}}
        aws-region: ${{{{ env.AWS_REGION }}}}
    
    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v1
    
    - name: Build, tag, and push image to Amazon ECR
      id: build-image
      env:
        ECR_REGISTRY: ${{{{ steps.login-ecr.outputs.registry }}}}
        IMAGE_TAG: ${{{{ github.sha }}}}
      run: |
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
        docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest
        echo "image=$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG" >> $GITHUB_OUTPUT
    
    - name: Scan Docker image
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: ${{{{ steps.build-image.outputs.image }}}}
        format: 'table'
        exit-code: '1'
        severity: 'CRITICAL,HIGH'
    
    - name: Update kubeconfig
      run: |
        aws eks update-kubeconfig --name ${{{{ env.EKS_CLUSTER }}}} --region ${{{{ env.AWS_REGION }}}}
    
    - name: Deploy to EKS
      env:
        IMAGE: ${{{{ steps.build-image.outputs.image }}}}
      run: |
        kubectl set image deployment/{app_name} {app_name}=$IMAGE -n ${{{{ env.NAMESPACE }}}}
        kubectl rollout status deployment/{app_name} -n ${{{{ env.NAMESPACE }}}} --timeout=5m
    
    - name: Verify deployment
      run: |
        kubectl get deployment {app_name} -n ${{{{ env.NAMESPACE }}}}
        kubectl get pods -n ${{{{ env.NAMESPACE }}}} -l app={app_name}
"""
        return workflow
    
    def generate_jenkins_pipeline(self, config: Dict[str, Any]) -> str:
        """Generate Jenkinsfile"""
        app_name = config.get("app_name", "agent-app")
        aws_region = config.get("aws_region", "us-east-1")
        ecr_repository = config.get("ecr_repository", app_name)
        cluster_name = config.get("cluster_name", "agent-cluster")
        namespace = config.get("namespace", "default")
        
        pipeline = f"""pipeline {{
    agent any
    
    environment {{
        AWS_REGION = '{aws_region}'
        ECR_REPOSITORY = '{ecr_repository}'
        EKS_CLUSTER = '{cluster_name}'
        NAMESPACE = '{namespace}'
        IMAGE_TAG = "${{BUILD_NUMBER}}"
    }}
    
    stages {{
        stage('Checkout') {{
            steps {{
                checkout scm
            }}
        }}
        
        stage('Test') {{
            steps {{
                sh '''
                    pip install -r requirements.txt
                    pip install pytest
                    pytest tests/ -v
                '''
            }}
        }}
        
        stage('Security Scan') {{
            steps {{
                sh '''
                    trivy fs --format json --output trivy-report.json .
                '''
            }}
        }}
        
        stage('Build Docker Image') {{
            steps {{
                script {{
                    withAWS(credentials: 'aws-credentials', region: env.AWS_REGION) {{
                        def ecrLogin = sh(script: 'aws ecr get-login-password', returnStdout: true).trim()
                        def ecrRegistry = sh(script: 'aws ecr describe-repositories --repository-names ${{ECR_REPOSITORY}} --query "repositories[0].repositoryUri" --output text | cut -d"/" -f1', returnStdout: true).trim()
                        
                        sh "docker login -u AWS -p ${{ecrLogin}} ${{ecrRegistry}}"
                        sh "docker build -t ${{ecrRegistry}}/${{ECR_REPOSITORY}}:${{IMAGE_TAG}} ."
                        sh "docker tag ${{ecrRegistry}}/${{ECR_REPOSITORY}}:${{IMAGE_TAG}} ${{ecrRegistry}}/${{ECR_REPOSITORY}}:latest"
                    }}
                }}
            }}
        }}
        
        stage('Push to ECR') {{
            steps {{
                script {{
                    withAWS(credentials: 'aws-credentials', region: env.AWS_REGION) {{
                        def ecrRegistry = sh(script: 'aws ecr describe-repositories --repository-names ${{ECR_REPOSITORY}} --query "repositories[0].repositoryUri" --output text | cut -d"/" -f1', returnStdout: true).trim()
                        sh "docker push ${{ecrRegistry}}/${{ECR_REPOSITORY}}:${{IMAGE_TAG}}"
                        sh "docker push ${{ecrRegistry}}/${{ECR_REPOSITORY}}:latest"
                    }}
                }}
            }}
        }}
        
        stage('Deploy to EKS') {{
            steps {{
                script {{
                    withAWS(credentials: 'aws-credentials', region: env.AWS_REGION) {{
                        sh "aws eks update-kubeconfig --name ${{EKS_CLUSTER}} --region ${{AWS_REGION}}"
                        def ecrRegistry = sh(script: 'aws ecr describe-repositories --repository-names ${{ECR_REPOSITORY}} --query "repositories[0].repositoryUri" --output text | cut -d"/" -f1', returnStdout: true).trim()
                        sh "kubectl set image deployment/{app_name} {app_name}=${{ecrRegistry}}/${{ECR_REPOSITORY}}:${{IMAGE_TAG}} -n ${{NAMESPACE}}"
                        sh "kubectl rollout status deployment/{app_name} -n ${{NAMESPACE}} --timeout=5m"
                    }}
                }}
            }}
        }}
    }}
    
    post {{
        always {{
            cleanWs()
        }}
        success {{
            echo 'Deployment successful!'
        }}
        failure {{
            echo 'Deployment failed!'
        }}
    }}
}}
"""
        return pipeline


cicd_service = CICDService()