"""Chat endpoints"""
from fastapi import APIRouter, HTTPException
import logging
import sys
from pathlib import Path

# Add parent directory to path to import utils
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages"))

from models import ChatRequest, ChatResponse
from services import get_ollama_service, get_chat_service
from utils import search_internet

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Generate chat response using Ollama"""
    try:
        ollama_service = get_ollama_service()
        chat_service = get_chat_service()
        
        # Build full prompt
        full_prompt = chat_service.build_full_prompt(
            request.prompt,
            request.messages
        )
        
        # Generate response
        result = ollama_service.generate_response(
            prompt=full_prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        if result.get('error'):
            raise HTTPException(
                status_code=503,
                detail=result.get('message')
            )
        
        # Calculate metrics
        response_text = result.get('response')
        inference_time = result.get('inference_time')
        
        prompt_tokens = len(full_prompt.split())
        response_tokens = len(response_text.split())
        tokens_per_second = response_tokens / inference_time if inference_time > 0 else 0
        
        logger.info(f"Inference time: {inference_time:.2f}s")
        logger.info(f"Tokens/second: {tokens_per_second:.1f}")
        
        return ChatResponse(
            response=response_text,
            inference_time=round(inference_time, 2),
            tokens_per_second=round(tokens_per_second, 1),
            prompt_tokens=prompt_tokens,
            response_tokens=response_tokens
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
