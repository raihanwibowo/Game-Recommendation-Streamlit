"""Ollama service for model interactions"""
import requests
import logging
import time
from typing import List, Dict
from config import settings
from models import Message

logger = logging.getLogger(__name__)


class OllamaService:
    """Service for interacting with Ollama"""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_URL
        self.model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT
    
    def get_available_models(self) -> List[str]:
        """Get list of available Ollama models"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model['name'] for model in models]
            return []
        except Exception as e:
            logger.error(f"Failed to get models: {e}")
            return []
    
    def check_connection(self) -> bool:
        """Check if Ollama is accessible"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def generate_response(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 800
    ) -> Dict:
        """Generate response from Ollama"""
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                        "num_ctx": 8192,           # Larger context window (default: 2048)
                        "top_k": 40,               # Consider top 40 tokens (more diverse)
                        "top_p": 0.9,              # Nucleus sampling (more coherent)
                        "repeat_penalty": 1.1,     # Reduce repetition
                        "presence_penalty": 0.0,   # Don't penalize new topics
                        "frequency_penalty": 0.0,  # Don't penalize frequent words
                        "mirostat": 0,             # Disable mirostat (use top_k/top_p)
                        "mirostat_tau": 5.0,       # Target perplexity
                        "mirostat_eta": 0.1,       # Learning rate
                        "num_thread": 8            # CPU threads (adjust based on your CPU)
                    }
                },
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                return {
                    "error": True,
                    "message": f"Ollama returned status {response.status_code}"
                }
            
            result = response.json()
            inference_time = time.time() - start_time
            
            return {
                "error": False,
                "response": result.get('response', ''),
                "inference_time": inference_time
            }
            
        except requests.exceptions.ConnectionError:
            return {
                "error": True,
                "message": "Cannot connect to Ollama. Make sure it's running."
            }
        except requests.exceptions.Timeout:
            return {
                "error": True,
                "message": "Request timed out."
            }
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return {
                "error": True,
                "message": str(e)
            }


# Singleton instance
_ollama_service = None

def get_ollama_service() -> OllamaService:
    """Get or create Ollama service instance"""
    global _ollama_service
    if _ollama_service is None:
        _ollama_service = OllamaService()
    return _ollama_service
