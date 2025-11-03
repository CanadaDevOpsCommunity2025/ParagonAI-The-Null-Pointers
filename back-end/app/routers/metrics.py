from fastapi import APIRouter
from datetime import datetime
from app.schemas import MetricsResponse

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("/")
async def test():
    return "Hello Theere"


@router.get("/{deployment_id}", response_model=MetricsResponse)
async def get_metrics(deployment_id: str):
    # Minimal mock implementation to keep API working
    return MetricsResponse(
        deployment_id=deployment_id,
        request_count=100,
        error_count=2,
        avg_response_time=0.35,
        uptime_percentage=99.5,
        last_updated=datetime.utcnow(),
    )

from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel
import pymongo
import logging
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/metrics", tags=["metrics"])

class ChartData(BaseModel):
    labels: List[str]
    datasets: List[dict]

@router.get("/requests/count", response_model=ChartData)
async def get_request_counts(
    time_range: str = "24h", 
    interval: str = "1h"
):
    try:
        logger.info(f"Fetching request counts for {time_range} with interval {interval}")
        
        client = pymongo.MongoClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=10000,        # 10 second connection timeout
            socketTimeoutMS=30000          # 30 second socket timeout
        )
        
        try:
            # Test the connection
            client.admin.command('ping')
            db = client[settings.MONGODB_DB]
            
            # Check if collection exists and has data
            if 'request_metrics' not in db.list_collection_names():
                logger.warning("request_metrics collection does not exist")
                return create_empty_response("No metrics data available")
            
            collection = db.request_metrics
            if collection.estimated_document_count() == 0:
                logger.warning("request_metrics collection is empty")
                return create_empty_response("No metrics data available")
            
            # Calculate time range
            end_time = datetime.utcnow()
            start_time = calculate_start_time(time_range, end_time)
            
            # Generate time buckets
            time_buckets = generate_time_buckets(start_time, end_time, interval)
            if not time_buckets:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid time range or interval"
                )
            
            # Rest of your aggregation pipeline...
            
        except pymongo.errors.ServerSelectionTimeoutError:
            logger.error("MongoDB connection timeout")
            raise HTTPException(
                status_code=503,
                detail="Database connection timeout"
            )
        finally:
            client.close()
            
    except Exception as e:
        logger.error(f"Error in get_request_counts: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

def create_empty_response(message: str) -> ChartData:
    """Helper to create an empty response with a message"""
    return ChartData(
        labels=[],
        datasets=[{
            "label": message,
            "data": [],
            "borderColor": "rgb(200, 200, 200)",
            "tension": 0.1
        }]
    )

def calculate_start_time(time_range: str, end_time: datetime) -> datetime:
    """Calculate start time based on time range"""
    if time_range == "1h":
        return end_time - timedelta(hours=1)
    elif time_range == "24h":
        return end_time - timedelta(days=1)
    elif time_range == "7d":
        return end_time - timedelta(days=7)
    elif time_range == "30d":
        return end_time - timedelta(days=30)
    return end_time - timedelta(days=1)  # Default to 24h

def generate_time_buckets(start: datetime, end: datetime, interval: str) -> List[datetime]:
    """Generate time buckets based on interval"""
    buckets = []
    current = start
    delta = parse_interval(interval)
    
    if not delta:
        return []
        
    while current <= end:
        buckets.append(current)
        current += delta
        
    return buckets

def parse_interval(interval: str) -> Optional[timedelta]:
    """Parse interval string into timedelta"""
    try:
        if interval.endswith('m'):
            return timedelta(minutes=int(interval[:-1]))
        elif interval.endswith('h'):
            return timedelta(hours=int(interval[:-1]))
        elif interval.endswith('d'):
            return timedelta(days=int(interval[:-1]))
    except ValueError:
        return None
    return None