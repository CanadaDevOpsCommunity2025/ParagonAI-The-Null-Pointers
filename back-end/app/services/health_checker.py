"""
Health checker service for deployed agents
"""

import httpx
from typing import Dict, Any
from datetime import datetime
from kubernetes import client, config
from app.config import settings


class HealthChecker:
    """Service for checking health of deployed agents"""
    
    def __init__(self):
        try:
            # Try to load kubeconfig
            config.load_incluster_config()
        except:
            try:
                config.load_kube_config()
            except:
                pass
    
    async def check_health(self, endpoint: str) -> Dict[str, Any]:
        """Check health of an agent endpoint"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as http_client:
                response = await http_client.get(f"{endpoint}/health")
                
                if response.status_code == 200:
                    return {
                        "healthy": True,
                        "status": response.json().get("status", "unknown"),
                        "checked_at": datetime.utcnow(),
                        "last_healthy": datetime.utcnow()
                    }
                else:
                    return {
                        "healthy": False,
                        "status": "unhealthy",
                        "checked_at": datetime.utcnow(),
                        "last_healthy": None
                    }
        except Exception as e:
            return {
                "healthy": False,
                "status": "error",
                "error": str(e),
                "checked_at": datetime.utcnow(),
                "last_healthy": None
            }
    
    async def get_k8s_metrics(
        self,
        deployment_name: str,
        namespace: str = "default"
    ) -> Dict[str, Any]:
        """Get Kubernetes metrics for a deployment"""
        try:
            v1 = client.CoreV1Api()
            apps_v1 = client.AppsV1Api()
            metrics_v1beta1 = client.CustomObjectsApi()
            
            # Get deployment
            deployment = apps_v1.read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace
            )
            
            # Get pods
            pods = v1.list_namespaced_pod(
                namespace=namespace,
                label_selector=f"app={deployment_name}"
            )
            
            replica_count = deployment.spec.replicas
            pod_count = len([p for p in pods.items if p.status.phase == "Running"])
            
            # Try to get resource metrics
            cpu_usage = 0.0
            memory_usage = 0.0
            
            try:
                # This requires metrics-server to be installed
                pod_metrics = metrics_v1beta1.list_namespaced_custom_object(
                    group="metrics.k8s.io",
                    version="v1beta1",
                    namespace=namespace,
                    plural="pods",
                    label_selector=f"app={deployment_name}"
                )
                
                total_cpu = 0
                total_memory = 0
                for pod_metric in pod_metrics.get("items", []):
                    for container in pod_metric.get("containers", []):
                        cpu = container.get("usage", {}).get("cpu", "0")
                        memory = container.get("usage", {}).get("memory", "0")
                        # Convert and sum (simplified)
                        total_cpu += self._parse_cpu(cpu)
                        total_memory += self._parse_memory(memory)
                
                cpu_usage = (total_cpu / replica_count * 100) if replica_count > 0 else 0
                memory_usage = (total_memory / replica_count * 100) if replica_count > 0 else 0
            except:
                # Metrics server not available, return defaults
                pass
            
            return {
                "pod_count": pod_count,
                "replica_count": replica_count,
                "cpu_usage_percent": cpu_usage,
                "memory_usage_percent": memory_usage
            }
        except Exception as e:
            print(f"Error getting K8s metrics: {e}")
            return {
                "pod_count": 0,
                "replica_count": 0,
                "cpu_usage_percent": None,
                "memory_usage_percent": None
            }
    
    def _parse_cpu(self, cpu_str: str) -> float:
        """Parse CPU string (e.g., '100m' or '1') to float"""
        if cpu_str.endswith('m'):
            return float(cpu_str[:-1]) / 1000
        return float(cpu_str)
    
    def _parse_memory(self, memory_str: str) -> float:
        """Parse memory string (e.g., '128Mi' or '1Gi') to MB"""
        if memory_str.endswith('Ki'):
            return float(memory_str[:-2]) / 1024
        elif memory_str.endswith('Mi'):
            return float(memory_str[:-2])
        elif memory_str.endswith('Gi'):
            return float(memory_str[:-2]) * 1024
        elif memory_str.endswith('K'):
            return float(memory_str[:-1]) / 1024
        elif memory_str.endswith('M'):
            return float(memory_str[:-1])
        elif memory_str.endswith('G'):
            return float(memory_str[:-1]) * 1024
        return float(memory_str)

