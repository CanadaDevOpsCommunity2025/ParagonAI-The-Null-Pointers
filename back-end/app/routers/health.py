"""
Health check router
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ParagonAI Backend",
        "version": "1.0.0"
    }

