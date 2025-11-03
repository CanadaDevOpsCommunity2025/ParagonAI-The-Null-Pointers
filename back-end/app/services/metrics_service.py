"""
Metrics Service - Updated for MongoDB/Beanie
Tracks and stores agent performance metrics
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from app.models import Metric, Deployment
from app.schemas import KPIResponse


class MetricsService:
    """Service for managing metrics"""
    
    async def record_metrics(
        self,
        deployment_id: str,
        metrics_data: Dict[str, Any]
    ) -> Metric:
        """Record new metrics entry"""
        metric = Metric(
            deployment_id=deployment_id,
            **metrics_data
        )
        await metric.insert()
        return metric
    
    async def get_latest_metrics(
        self,
        deployment_id: str
    ) -> Optional[Metric]:
        """Get latest metrics for a deployment"""
        # Sort by timestamp descending
        metrics = await Metric.find(
            Metric.deployment_id == deployment_id
        ).sort([("timestamp", -1)]).limit(1).to_list()
        return metrics[0] if metrics else None
    
    async def get_metrics_history(
        self,
        deployment_id: str,
        hours: int = 24
    ) -> List[Metric]:
        """Get metrics history for a deployment"""
        since = datetime.utcnow() - timedelta(hours=hours)
        return await Metric.find(
            Metric.deployment_id == deployment_id,
            Metric.timestamp >= since
        ).sort([("timestamp", -1)]).to_list()
    
    async def calculate_kpis(
        self,
        deployment_id: str
    ) -> KPIResponse:
        """Calculate Key Performance Indicators"""
        # Get all metrics for this deployment
        metrics = await Metric.find(
            Metric.deployment_id == deployment_id
        ).to_list()
        
        if not metrics:
            # Return default KPIs
            return KPIResponse(
                deployment_id=deployment_id,
                total_requests=0,
                success_rate=0.0,
                average_response_time=0.0,
                uptime_percentage=100.0,
                total_downtime_minutes=0.0,
                current_status="unknown",
                health_status="unknown",
                resource_usage={}
            )
        
        # Calculate aggregates
        total_requests = sum(m.request_count for m in metrics)
        total_success = sum(m.success_count for m in metrics)
        
        success_rate = (total_success / total_requests * 100) if total_requests > 0 else 0.0
        
        # Average response times
        response_times = [m.average_response_time for m in metrics if m.average_response_time]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0
        
        # Uptime calculation
        uptime_values = [m.uptime_percentage for m in metrics if m.uptime_percentage is not None]
        avg_uptime = sum(uptime_values) / len(uptime_values) if uptime_values else 100.0
        
        # Downtime
        downtime_values = [m.downtime_minutes for m in metrics if m.downtime_minutes is not None]
        total_downtime = sum(downtime_values)
        
        # Current status from deployment
        deployment = await Deployment.find_one(
            Deployment.deployment_id == deployment_id
        )
        current_status = deployment.status.value if deployment else "unknown"
        
        # Health status from latest metric
        latest_metric = await self.get_latest_metrics(deployment_id)
        health_status = "healthy" if (latest_metric and latest_metric.is_healthy) else "unhealthy"
        
        # Resource usage (average)
        cpu_values = [m.cpu_usage_percent for m in metrics if m.cpu_usage_percent is not None]
        memory_values = [m.memory_usage_percent for m in metrics if m.memory_usage_percent is not None]
        
        avg_cpu = sum(cpu_values) / len(cpu_values) if cpu_values else 0.0
        avg_memory = sum(memory_values) / len(memory_values) if memory_values else 0.0
        
        return KPIResponse(
            deployment_id=deployment_id,
            total_requests=total_requests,
            success_rate=round(success_rate, 2),
            average_response_time=round(avg_response_time, 2),
            uptime_percentage=round(avg_uptime, 2),
            total_downtime_minutes=round(total_downtime, 2),
            current_status=current_status,
            health_status=health_status,
            resource_usage={
                "cpu_percent": round(avg_cpu, 2),
                "memory_percent": round(avg_memory, 2)
            }
        )
