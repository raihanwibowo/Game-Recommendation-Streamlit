"""Health and status endpoints"""
from fastapi import APIRouter
from datetime import datetime
from models import HealthResponse, ModelInfo, ServiceInfo
from services import get_ollama_service
from config import settings

router = APIRouter(tags=["health"])


@router.get("/", response_model=ServiceInfo)
async def root():
    """Root endpoint with service information"""
    return ServiceInfo(
        service=settings.API_TITLE,
        status="running",
        version=settings.API_VERSION
    )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    ollama_service = get_ollama_service()
    ollama_status = "connected" if ollama_service.check_connection() else "disconnected"
    
    return HealthResponse(
        status="healthy",
        ollama=ollama_status,
        timestamp=datetime.now().isoformat()
    )


@router.get("/models", response_model=ModelInfo)
async def get_models():
    """Get available Ollama models"""
    ollama_service = get_ollama_service()
    
    model_names = ollama_service.get_available_models()
    model_name = settings.OLLAMA_MODEL
    
    return ModelInfo(
        name=model_name,
        available=model_name in model_names,
        models=model_names
    )
