"""
GenAgent Core utility - Code generation logic
"""

import json
import os
from typing import Dict, Any, Optional
from jinja2 import Template

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class GenAgentCore:
    """Core code generation logic for agent deployment"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.llm_client = None
        
        if self.api_key and OPENAI_AVAILABLE:
            try:
                self.llm_client = openai.OpenAI(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI client: {e}")
    
    def parse_prompt(self, prompt: str) -> Dict[str, Any]:
        """Parse user prompt to extract deployment requirements"""
        if not self.llm_client:
            return self._template_based_parse(prompt)
        
        try:
            system_prompt = """You are an expert DevOps engineer. Parse the user's deployment request and extract:
- agent_type: customer_support, content_writer, or data_analyst
- cloud_provider: aws, azure, gcp, or local
- scale: number of replicas (default: 2)
- monitoring: true/false
- api_endpoint: whether to expose API endpoint
- container_platform: docker, kubernetes, or both

Return a JSON object with these fields."""
            
            response = self.llm_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error parsing prompt with LLM: {e}")
            return self._template_based_parse(prompt)
    
    def _template_based_parse(self, prompt: str) -> Dict[str, Any]:
        """Fallback template-based parsing"""
        prompt_lower = prompt.lower()
        return {
            "agent_type": "customer_support" if "support" in prompt_lower else 
                         "content_writer" if "content" in prompt_lower else
                         "data_analyst" if "data" in prompt_lower else "customer_support",
            "cloud_provider": "aws" if "aws" in prompt_lower else
                            "azure" if "azure" in prompt_lower else
                            "gcp" if "gcp" in prompt_lower else "local",
            "scale": 2,
            "monitoring": "monitor" in prompt_lower or "grafana" in prompt_lower,
            "api_endpoint": True,
            "container_platform": "kubernetes" if "kubernetes" in prompt_lower or "k8s" in prompt_lower else "docker"
        }
