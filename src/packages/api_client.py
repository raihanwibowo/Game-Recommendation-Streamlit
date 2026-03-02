"""API client for backend communication"""
import requests
import logging
import os
from typing import List, Dict

logger = logging.getLogger(__name__)


class GameRecommendationAPIClient:
    """Client for Game Recommendation API"""
    
    def __init__(self):
        """Initialize API client"""
        self.base_url = os.getenv('API_URL', 'http://localhost:8000')
        self.timeout = 180
    
    def health_check(self) -> Dict:
        """Check API health"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_models(self) -> Dict:
        """Get available models"""
        try:
            response = requests.get(
                f"{self.base_url}/models",
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get models: {e}")
            return {"name": "unknown", "available": False, "models": []}
    
    def chat(
        self,
        prompt: str,
        messages: List[Dict],
        use_search: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 800
    ) -> Dict:
        """Send chat request to API"""
        try:
            payload = {
                "prompt": prompt,
                "messages": messages,
                "use_search": use_search,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            logger.info(f"Sending chat request to {self.base_url}/chat")
            
            response = requests.post(
                f"{self.base_url}/chat",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                error_detail = response.json().get('detail', 'Unknown error')
                logger.error(f"API error: {error_detail}")
                return {
                    "error": True,
                    "message": error_detail
                }
            
            result = response.json()
            logger.info(f"Response received: {result.get('inference_time')}s")
            
            return {
                "error": False,
                "response": result.get('response'),
                "inference_time": result.get('inference_time'),
                "tokens_per_second": result.get('tokens_per_second'),
                "prompt_tokens": result.get('prompt_tokens'),
                "response_tokens": result.get('response_tokens')
            }
            
        except requests.exceptions.ConnectionError:
            error_msg = f"Cannot connect to API at {self.base_url}. Make sure the backend is running."
            logger.error(error_msg)
            return {"error": True, "message": error_msg}
        
        except requests.exceptions.Timeout:
            error_msg = "Request timed out. Try a faster model or reduce max_tokens."
            logger.error(error_msg)
            return {"error": True, "message": error_msg}
        
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return {"error": True, "message": error_msg}


# Singleton instance
_api_client = None

def get_api_client() -> GameRecommendationAPIClient:
    """Get or create API client instance"""
    global _api_client
    if _api_client is None:
        _api_client = GameRecommendationAPIClient()
    return _api_client
