"""
Background task for collecting metrics from deployed agents
"""

import asyncio
from typing import Dict, Any
from datetime import datetime, timedelta
from app.models import Deployment, Metric, DeploymentStatus
from app.services.metrics_service import MetricsService
from app.services.health_checker import HealthChecker
import httpx


class MetricsCollector:
    """Background task to collect metrics from deployed agents"""
    
    def __init__(self):
        self.running = False
        self.task = None
        self.metrics_service = MetricsService()
        self.health_checker = HealthChecker()
    
    async def start(self):
        """Start the metrics collector"""
        self.running = True
        self.task = asyncio.create_task(self._collect_loop())
    
    async def stop(self):
        """Stop the metrics collector"""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
    
    async def _collect_loop(self):
        """Main collection loop"""
        while self.running:
            try:
                # Get all running deployments
                deployments = await Deployment.find(
                    Deployment.status == DeploymentStatus.RUNNING
                ).to_list()
                
                for deployment in deployments:
                    try:
                        await self._collect_deployment_metrics(deployment)
                    except Exception as e:
                        print(f"Error collecting metrics for {deployment.deployment_id}: {e}")
                
                # Wait 30 seconds before next collection
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in metrics collector loop: {e}")
                await asyncio.sleep(30)
    
    async def _collect_deployment_metrics(self, deployment: Deployment):
        """Collect metrics for a single deployment"""
        if not deployment.service_endpoint:
            return
        
        try:
            # Health check
            health_status = await self.health_checker.check_health(
                deployment.service_endpoint
            )
            
            # Get metrics from agent endpoint
            async with httpx.AsyncClient(timeout=10.0) as client:
                try:
                    metrics_response = await client.get(
                        f"{deployment.service_endpoint}/metrics"
                    )
                    agent_metrics = metrics_response.json() if metrics_response.status_code == 200 else {}
                except:
                    agent_metrics = {}
            
            # Get Kubernetes metrics (pod status, resource usage)
            k8s_metrics = await self.health_checker.get_k8s_metrics(
                deployment.deployment_id,
                deployment.eks_namespace or "default"
            )
            
            # Calculate response time percentiles
            response_times = agent_metrics.get("response_times", [])
            p50 = self._percentile(response_times, 50) if response_times else None
            p95 = self._percentile(response_times, 95) if response_times else None
            p99 = self._percentile(response_times, 99) if response_times else None
            
            # Calculate uptime
            uptime_percentage = 100.0 if health_status["healthy"] else 0.0
            downtime_minutes = 0.0 if health_status["healthy"] else (
                (datetime.utcnow() - health_status.get("last_healthy", datetime.utcnow())).total_seconds() / 60
            )
            
            # Create metrics document
            metric = Metric(
                deployment_id=deployment.deployment_id,
                request_count=agent_metrics.get("request_count", 0),
                success_count=agent_metrics.get("success_count", 0),
                error_count=agent_metrics.get("error_count", 0),
                average_response_time=agent_metrics.get("average_response_time_ms"),
                p50_response_time=p50,
                p95_response_time=p95,
                p99_response_time=p99,
                uptime_percentage=uptime_percentage,
                downtime_minutes=downtime_minutes,
                last_health_check=datetime.utcnow(),
                is_healthy=health_status["healthy"],
                cpu_usage_percent=k8s_metrics.get("cpu_usage_percent"),
                memory_usage_percent=k8s_metrics.get("memory_usage_percent"),
                pod_count=k8s_metrics.get("pod_count"),
                replica_count=k8s_metrics.get("replica_count")
            )
            
            await metric.insert()
            
        except Exception as e:
            print(f"Error collecting metrics for {deployment.deployment_id}: {e}")
    
    def _percentile(self, data: list, percentile: int) -> float:
        """Calculate percentile from list"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]


# Global instance
_metrics_collector = MetricsCollector()


async def start_metrics_collector():
    """Start the global metrics collector"""
    await _metrics_collector.start()


async def stop_metrics_collector():
    """Stop the global metrics collector"""
    await _metrics_collector.stop()

