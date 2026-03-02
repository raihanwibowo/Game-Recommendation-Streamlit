"""Configuration management"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings"""
    
    # API Settings
    API_TITLE = "Game Recommendation API"
    API_DESCRIPTION = "Ollama-powered game recommendation service"
    API_VERSION = "1.0.0"
    
    # Ollama Settings
    OLLAMA_URL: str = os.getenv('OLLAMA_URL', 'http://localhost:11434')
    OLLAMA_MODEL: str = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')
    OLLAMA_TIMEOUT: int = 180
    
    # Database Settings
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'postgresql://localhost/game_recommendation')
    
    # CORS Settings
    CORS_ORIGINS = ["*"]  # In production, specify your frontend URL
    
    # Logging
    LOG_LEVEL = "INFO"


settings = Settings()
