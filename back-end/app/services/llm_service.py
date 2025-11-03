class LLMService:
    def parse_deployment_prompt(self, prompt: str):
        # Minimal heuristic parser
        agent_type = "customer_support" if "support" in prompt.lower() else (
            "content_writer" if "content" in prompt.lower() else "data_analyst"
        )
        return {
            "agent_type": agent_type,
            "scale_requirements": {"replicas": 1},
        }

    def generate_agent_code(self, agent_type: str, requirements: dict) -> str:
        return (
            "from fastapi import FastAPI\n"
            "app = FastAPI()\n\n"
            "@app.get('/health')\n"
            "def health():\n"
            "    return {'status': 'ok', 'agent_type': '" + agent_type + "'}\n"
        )


llm_service = LLMService()

from openai import OpenAI
from app.config import settings
from typing import Dict, Any
import json


class LLMService:
    def __init__(self):
        if settings.DEFAULT_LLM_PROVIDER == "groq":
            self.client = OpenAI(
                api_key=settings.GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1",
            )
        elif settings.DEFAULT_LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            raise ValueError("No valid LLM provider configured")
    
    def parse_deployment_prompt(self, prompt: str) -> Dict[str, Any]:
        """Parse user prompt to extract deployment requirements"""
        system_prompt = """You are an expert DevOps assistant. Parse the user's deployment request and extract:
        - agent_type: customer_support, content_writer, or data_analyst
        - cloud_provider: aws, azure, gcp, or onprem
        - scale_requirements: number of replicas, auto-scaling needs
        - monitoring_needs: whether they need observability
        - security_requirements: any specific security needs
        
        Return ONLY valid JSON with these fields. Infer reasonable defaults if not specified."""
        
        response = self.client.chat.completions.create(
            model=settings.DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
        )
        
        try:
            parsed = json.loads(response.choices[0].message.content)
            return parsed
        except json.JSONDecodeError:
            return {
                "agent_type": "customer_support",
                "cloud_provider": "aws",
                "scale_requirements": {"replicas": 1, "auto_scale": False},
                "monitoring_needs": True,
                "security_requirements": {"enable_scan": True}
            }
    
    def generate_agent_code(self, agent_type: str, requirements: Dict[str, Any]) -> str:
        """Generate Python agent code based on type and requirements"""
        system_prompt = f"""Generate production-ready Python code for a {agent_type} agent using FastAPI and LangChain.
        Include:
        - FastAPI app with /chat and /health endpoints
        - LangChain agent setup
        - Error handling and logging
        - Environment variable configuration
        
        Return ONLY the Python code, no explanations."""
        
        response = self.client.chat.completions.create(
            model=settings.DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(requirements)}
            ],
            temperature=0.2,
        )
        
        return response.choices[0].message.content
    
    def generate_dockerfile(self, agent_code: str, requirements: Dict[str, Any]) -> str:
        """Generate optimized Dockerfile for the agent"""
        system_prompt = """Generate an optimized Dockerfile for a Python FastAPI application.
        Use multi-stage builds, minimal base image, and best practices.
        Return ONLY the Dockerfile content, no explanations."""
        
        response = self.client.chat.completions.create(
            model=settings.DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Requirements: {json.dumps(requirements)}"}
            ],
            temperature=0.1,
        )
        
        return response.choices[0].message.content


llm_service = LLMService()