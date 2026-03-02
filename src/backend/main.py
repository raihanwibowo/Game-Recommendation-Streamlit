"""FastAPI backend for Ollama game recommendation service"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import requests
import os
import logging
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Game Recommendation API",
    description="Ollama-powered game recommendation service",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Streamlit URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    prompt: str
    messages: List[Message]
    use_search: bool = False
    temperature: float = 0.7
    max_tokens: int = 800


class ChatResponse(BaseModel):
    response: str
    inference_time: float
    tokens_per_second: float
    prompt_tokens: int
    response_tokens: int


class ModelInfo(BaseModel):
    name: str
    available: bool
    models: List[str]


# Helper functions
def get_ollama_url():
    """Get Ollama URL from environment"""
    return os.getenv('OLLAMA_URL', 'http://localhost:11434')


def get_ollama_model():
    """Get Ollama model from environment"""
    return os.getenv('OLLAMA_MODEL', 'llama3.2:3b')


def build_conversation_context(messages: List[Message]) -> str:
    """Build conversation context from messages"""
    context = ""
    
    # Summarize old messages if more than 10
    if len(messages) > 10:
        old_messages = messages[:-10]
        user_preferences = []
        games_discussed = []
        
        for msg in old_messages:
            content = msg.content.lower()
            if msg.role == 'user':
                if any(word in content for word in ['like', 'love', 'prefer', 'favorite', 'suka', 'favorit']):
                    user_preferences.append(msg.content[:100])
                
                words = msg.content.split()
                for word in words:
                    if len(word) > 3 and word[0].isupper():
                        games_discussed.append(word)
        
        if user_preferences or games_discussed:
            context += "\n--- CONVERSATION SUMMARY (Older Messages) ---\n"
            if user_preferences:
                context += "User Preferences:\n"
                for pref in user_preferences[:5]:
                    context += f"- {pref}\n"
            if games_discussed:
                unique_games = list(set(games_discussed))[:10]
                context += f"\nGames Discussed: {', '.join(unique_games)}\n"
            context += "--- END SUMMARY ---\n\n"
    
    # Add recent messages
    recent_messages = messages[-10:] if len(messages) > 10 else messages
    if recent_messages:
        context += "\n--- RECENT CONVERSATION (Full Detail) ---\n"
        for msg in recent_messages:
            context += f"{msg.role.capitalize()}: {msg.content}\n\n"
        context += "--- END RECENT CONVERSATION ---\n\n"
    
    return context


def get_system_message() -> str:
    """Get system message for the model"""
    return """You are a gaming expert AI assistant specializing ONLY in video game recommendations and gaming topics.

STRICT RULES:
1. ONLY answer questions about video games, gaming platforms, game recommendations, gaming hardware, and gaming culture
2. If asked about non-gaming topics (politics, health, finance, general knowledge, etc.), politely decline and redirect to gaming
3. Examples of acceptable topics: game recommendations, game reviews, gaming tips, platform comparisons, gaming news
4. Examples of unacceptable topics: cooking, math problems, history, science, personal advice (unless gaming-related)

LANGUAGE RULES:
- ALWAYS respond in the SAME LANGUAGE as the user's question
- If user asks in English, respond in English
- If user asks in Bahasa Indonesia, respond in Bahasa Indonesia
- Match the user's language naturally and fluently

RESPONSE FORMAT:
- If the question is about games: Answer enthusiastically with detailed gaming knowledge IN THE USER'S LANGUAGE
- If the question is NOT about games in English: "I'm a gaming specialist AI! I can only help with video game recommendations and gaming-related questions. Ask me about games, gaming platforms, or what to play next! 🎮"
- If the question is NOT about games in Bahasa Indonesia: "Saya adalah AI spesialis gaming! Saya hanya bisa membantu dengan rekomendasi video game dan pertanyaan seputar gaming. Tanyakan tentang game, platform gaming, atau game apa yang harus dimainkan selanjutnya! 🎮"

Use your conversation history as your knowledge base - remember what you've already discussed about games.
Be conversational, enthusiastic, and knowledgeable about gaming."""


# API endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Game Recommendation API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        ollama_url = get_ollama_url()
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        ollama_status = "connected" if response.status_code == 200 else "disconnected"
    except:
        ollama_status = "disconnected"
    
    return {
        "status": "healthy",
        "ollama": ollama_status,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/models", response_model=ModelInfo)
async def get_models():
    """Get available Ollama models"""
    try:
        ollama_url = get_ollama_url()
        model_name = get_ollama_model()
        
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            return ModelInfo(
                name=model_name,
                available=model_name in model_names,
                models=model_names
            )
        else:
            return ModelInfo(name=model_name, available=False, models=[])
    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Generate chat response using Ollama"""
    try:
        start_time = time.time()
        
        ollama_url = get_ollama_url()
        model = get_ollama_model()
        
        # Build context
        conversation_context = build_conversation_context(request.messages)
        system_message = get_system_message()
        
        # Build full prompt
        full_prompt = f"{system_message}{conversation_context}\n\nUser: {request.prompt}\n\nAssistant:"
        
        prompt_tokens = len(full_prompt.split())
        logger.info(f"Prompt size: ~{prompt_tokens} tokens")
        
        # Call Ollama
        inference_start = time.time()
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": request.temperature,
                    "num_predict": request.max_tokens
                }
            },
            timeout=180
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Ollama returned status {response.status_code}"
            )
        
        result = response.json()
        full_response = result.get('response', '')
        
        # Calculate metrics
        inference_time = time.time() - inference_start
        response_tokens = len(full_response.split())
        tokens_per_second = response_tokens / inference_time if inference_time > 0 else 0
        
        logger.info(f"Inference time: {inference_time:.2f}s")
        logger.info(f"Tokens/second: {tokens_per_second:.1f}")
        
        return ChatResponse(
            response=full_response,
            inference_time=round(inference_time, 2),
            tokens_per_second=round(tokens_per_second, 1),
            prompt_tokens=prompt_tokens,
            response_tokens=response_tokens
        )
        
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Cannot connect to Ollama. Make sure it's running with 'ollama serve'"
        )
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=504,
            detail="Request timed out. Try a faster model or reduce max_tokens."
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
