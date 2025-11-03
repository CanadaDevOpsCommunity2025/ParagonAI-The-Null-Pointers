"""
MongoDB database setup and connection management
"""

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from app.models import Deployment, Metric


class MongoDB:
    client: AsyncIOMotorClient = None
    database = None


mongodb = MongoDB()


async def init_db():
    """Initialize MongoDB connection and Beanie ODM"""
    mongodb.client = AsyncIOMotorClient(settings.MONGODB_URL)
    mongodb.database = mongodb.client[settings.MONGODB_DB_NAME]
    
    # Initialize Beanie with document models
    await init_beanie(
        database=mongodb.database,
        document_models=[Deployment, Metric]
    )
    print("✅ MongoDB connected and Beanie initialized")


async def close_db():
    """Close MongoDB connection"""
    if mongodb.client:
        mongodb.client.close()
        print("✅ MongoDB connection closed")


def get_database():
    """Get database instance"""
    return mongodb.database
