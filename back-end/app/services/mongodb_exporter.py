class MongoDBExporter:
    def __init__(self, mongo_uri: str, db_name: str, port: int = 8001):
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.port = port

    def run(self):
        # Stub exporter: no-op to keep server startup working without dependencies
        return

# app/services/mongodb_exporter.py
from prometheus_client import start_http_server, Gauge, Counter
import pymongo
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MongoDBExporter:
    def __init__(self, mongo_uri, db_name='metrics', port=8001):
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.port = port
        
        # Define Prometheus metrics
        self.request_count = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status']
        )
        
        self.response_time = Gauge(
            'http_response_time_seconds',
            'HTTP response time in seconds',
            ['endpoint']
        )
        
        self.error_count = Counter(
            'http_errors_total',
            'Total HTTP errors',
            ['endpoint', 'status_code']
        )
        
        self.active_deployments = Gauge(
            'active_deployments',
            'Number of active deployments'
        )
        
        self.client = None
        self.db = None
        
    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = pymongo.MongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            logger.info("Connected to MongoDB")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
    
    def collect_metrics(self):
        """Collect metrics from MongoDB and update Prometheus metrics"""
        if self.db is None:
            self.connect()
            if self.db is None:
                return
                
        try:
            # Get request counts by endpoint
            pipeline = [
                {"$group": {
                    "_id": {"endpoint": "$endpoint", "status": "$status"},
                    "count": {"$sum": 1}
                }}
            ]
            
            results = list(self.db.request_metrics.aggregate(pipeline))
            for result in results:
                self.request_count.labels(
                    method=result['_id'].get('method', 'unknown'),
                    endpoint=result['_id']['endpoint'],
                    status=result['_id']['status']
                ).set(result['count'])
            
            # Get active deployments count
            active_count = self.db.deployments.count_documents({
                "status": "running"
            })
            self.active_deployments.set(active_count)
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
    
    def run(self):
        """Start the metrics server and collection loop"""
        start_http_server(self.port)
        logger.info(f"Prometheus metrics server started on port {self.port}")
        
        while True:
            self.collect_metrics()
            time.sleep(15)  # Collect metrics every 15 seconds