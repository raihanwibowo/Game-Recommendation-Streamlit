"""Pydantic models for request/response validation"""
from pydantic import BaseModel
from typing import List, Optional


class Message(BaseModel):
    """Chat message model"""
    role: str
    content: str


class ChatRequest(BaseModel):
    """Chat request model"""
    prompt: str
    messages: List[Message]
    use_search: bool = False
    temperature: float = 0.7
    max_tokens: int = 800


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    inference_time: float
    tokens_per_second: float
    prompt_tokens: int
    response_tokens: int


class ModelInfo(BaseModel):
    """Model information"""
    name: str
    available: bool
    models: List[str]


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    ollama: str
    timestamp: str


class ServiceInfo(BaseModel):
    """Service information"""
    service: str
    status: str
    version: str
